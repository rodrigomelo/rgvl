"""
Receita Federal Collector - Queries CNPJ data via public APIs
Looks up company registration, partners, and activity codes.
"""

import json
import re
import time
import httpx

from data.collectors.base import BaseCollector


class ReceitaFederalCollector(BaseCollector):
    """Look up CNPJ data from Receita Federal public API."""
    NAME = "receita_federal"
    DESCRIPTION = "Query CNPJ data from Receita Federal"

    # Public CNPJ APIs (free, no auth required)
    APIS = [
        "https://publica.cnpj.ws/cnpj/{cnpj}",           # CNPJ.ws (free)
        "https://brasilapi.com.br/api/cnpj/v1/{cnpj}",    # BrasilAPI (free)
        "https://receitaws.com.br/v1/cnpj/{cnpj}",        # ReceitaWS (free tier)
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    def _clean_cnpj(self, cnpj):
        """Remove formatting from CNPJ."""
        return re.sub(r'[^0-9]', '', cnpj)

    def _query_cnpj(self, client, cnpj_raw):
        """Query CNPJ from multiple APIs with fallback."""
        cnpj = self._clean_cnpj(cnpj_raw)
        if len(cnpj) != 14:
            self.log(f"Invalid CNPJ: {cnpj_raw}", "warn")
            return None

        # Try CNPJ.ws first (most reliable, no rate limit)
        urls = [
            f"https://publica.cnpj.ws/cnpj/{cnpj}",
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}",
        ]

        for url in urls:
            try:
                resp = client.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    return self._normalize_cnpjws(data, cnpj)
                elif resp.status_code == 429:
                    self.log(f"Rate limited on {url.split('/')[2]}, waiting...", "warn")
                    time.sleep(3)
            except httpx.HTTPError as e:
                self.log(f"API error: {e}", "warn")
                continue

        return None

    def _normalize_cnpjws(self, data, cnpj):
        """Normalize CNPJ.ws response into standard format."""
        estabelecimento = data.get("estabelecimento", {})
        empresa = data.get("empresa", {})

        return {
            "cnpj": cnpj,
            "razao_social": empresa.get("razao_social", ""),
            "nome_fantasia": estabelecimento.get("nome_fantasia", ""),
            "situacao_cadastral": estabelecimento.get("situacao_cadastral", ""),
            "data_situacao_cadastral": estabelecimento.get("data_situacao_cadastral", ""),
            "natureza_juridica": empresa.get("natureza_juridica", {}).get("descricao", ""),
            "data_abertura": estabelecimento.get("data_inicio_atividade", ""),
            "cnae_principal": estabelecimento.get("atividade_principal", {}).get("codigo", ""),
            "cnae_descricao": estabelecimento.get("atividade_principal", {}).get("descricao", ""),
            "logradouro": estabelecimento.get("logradouro", ""),
            "numero": estabelecimento.get("numero", ""),
            "complemento": estabelecimento.get("complemento", ""),
            "bairro": estabelecimento.get("bairro", ""),
            "municipio": estabelecimento.get("cidade", {}).get("descricao", ""),
            "uf": estabelecimento.get("estado", {}).get("sigla", ""),
            "cep": estabelecimento.get("cep", ""),
            "telefone1": estabelecimento.get("telefone1", ""),
            "email": estabelecimento.get("email", ""),
            "capital_social": empresa.get("capital_social", 0),
            "porte": empresa.get("porte", {}).get("descricao", ""),
            "socios": [
                {
                    "nome": s.get("pessoa", {}).get("nome", ""),
                    "qualificacao": s.get("qualificacao_socio", {}).get("descricao", ""),
                    "data_entrada": s.get("data_entrada", ""),
                }
                for s in empresa.get("socios", [])
            ],
            "source_api": "cnpj.ws",
        }

    def collect(self):
        """Look up all companies with valid CNPJs."""
        session = self._get_session()
        models = self._get_models()

        # Get all companies from DB
        companies = session.query(models.Company).all()
        client = httpx.Client(headers=self.HEADERS, follow_redirects=True, timeout=20)

        try:
            for company in companies:
                cnpj = company.cnpj if hasattr(company, 'cnpj') else None
                if not cnpj or cnpj.startswith("00.000.000"):
                    self.log(f"Skipping {company.trade_name or company.id} — no valid CNPJ", "warn")
                    continue

                self.log(f"Querying CNPJ: {cnpj} ({company.trade_name or ''})")

                data = self._query_cnpj(client, cnpj)
                if data:
                    self.log(f"  Found: {data.get('razao_social', '')} — {data.get('situacao_cadastral', '')}", "success")
                    self.log(f"  Address: {data.get('logradouro', '')}, {data.get('numero', '')} - {data.get('municipio', '')}/{data.get('uf', '')}")

                    # Save as insight
                    self.save_insight(
                        category="company_registration",
                        title=f"CNPJ {cnpj}: {data.get('nome_fantasia') or data.get('razao_social', '')}",
                        content=json.dumps(data, ensure_ascii=False, indent=2)[:1000],
                        source="receita_federal",
                    )

                    # Update company record if possible
                    if data.get("situacao_cadastral"):
                        company.registration_status = data["situacao_cadastral"]

                    # Save socios as profiles
                    for socio in data.get("socios", []):
                        nome = socio.get("nome", "")
                        if nome:
                            self.save_profile(
                                source="receita_federal",
                                external_id=f"{cnpj}-socio-{nome[:20]}",
                                name=nome,
                                bio=f"Sócio de {data.get('nome_fantasia') or data.get('razao_social')}. "
                                    f"Qualificação: {socio.get('qualificacao', '')}. "
                                    f"Entrada: {socio.get('data_entrada', '')}",
                                raw_data=socio,
                            )

                    time.sleep(2)  # Rate limit
                else:
                    self.log(f"  No data found", "warn")

        finally:
            client.close()
