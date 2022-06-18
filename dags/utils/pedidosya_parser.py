"Pedidos Ya HTML Parser"


class PedidosYaParser:
    def __init__(self, html_body):
        self.html_body = html_body

    def get_shipping_amount(self):
        trs = self.html_body.find_all("tr")

        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                trs2 = td.find_all("tr")
                for tr2 in trs2:
                    spans = tr2.find_all("span")
                    if "envío" in "".join(map(str, list(spans))).lower():
                        for span in spans:
                            text = span.text.strip()
                            if "$" in text:
                                return float(text.replace("$", ""))

    def get_tip_amount(self):
        trs = self.html_body.find_all("tr")

        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                trs2 = td.find_all("tr")
                for tr2 in trs2:
                    spans = tr2.find_all("span")
                    if "Propina" in "".join(map(str, list(spans))):
                        for span in spans:
                            text = span.text.strip()
                            if "$" in text:
                                return float(text.replace("$", ""))

    def get_subtotal_amount(self):
        trs = self.html_body.find_all("tr")

        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                trs2 = td.find_all("tr")
                for tr2 in trs2:
                    spans = tr2.find_all("span")
                    if (
                        "sub-total" in "".join(map(str, list(spans))).lower()
                        or "subtotal" in "".join(map(str, list(spans))).lower()
                    ):
                        for span in spans:
                            text = span.text.strip()
                            if "$" in text:
                                return float(text.replace("$", ""))

    def get_discount_amount(self):
        trs = self.html_body.find_all("tr")

        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                trs2 = td.find_all("tr")
                for tr2 in trs2:
                    spans = tr2.find_all("span")
                    if "descuento" in "".join(map(str, list(spans))).lower():
                        for span in spans:
                            text = span.text.strip()
                            if "$" in text:
                                return float(text.replace("$", ""))

    def get_total_amount(self):
        trs = self.html_body.find_all("tr")

        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                trs2 = td.find_all("tr")
                for tr2 in trs2:
                    spans = tr2.find_all("span")
                    if "Total" in "".join(map(str, list(spans))):
                        for span in spans:
                            text = span.text.strip()
                            if "$" in text:
                                return float(text.replace("$", ""))

    def get_payment_method(self):
        trs = self.html_body.find_all("tr")

        span_results = []
        # Get Total amount
        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                trs2 = td.find_all("tr")
                for tr2 in trs2:
                    spans = tr2.find_all("span")
                    for span in spans:
                        text = span.text.strip()
                        span_results.append(text)

        if span_results[-4] != "El equipo de PedidosYa":
            return span_results[-4]
        else:
            return span_results[-9]
