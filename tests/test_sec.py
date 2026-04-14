from market_intelligence_rag.sec import _extract_selected_exhibit_links


def test_extract_selected_exhibit_links_finds_99_1() -> None:
    html = """
    <html>
      <body>
        <table class="tableFile">
          <tr>
            <th>Seq</th><th>Description</th><th>Document</th><th>Type</th><th>Size</th>
          </tr>
          <tr>
            <td>1</td>
            <td>8-K</td>
            <td><a href="/ix?doc=/Archives/edgar/data/1018724/000101872426000002/amzn-20260205.htm">amzn-20260205.htm</a></td>
            <td>8-K</td>
            <td>33976</td>
          </tr>
          <tr>
            <td>2</td>
            <td>EX-99.1</td>
            <td><a href="/Archives/edgar/data/1018724/000101872426000002/amzn-20251231xex991.htm">amzn-20251231xex991.htm</a></td>
            <td>EX-99.1</td>
            <td>629318</td>
          </tr>
        </table>
      </body>
    </html>
    """
    matches = _extract_selected_exhibit_links(
        html,
        "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000002/0001018724-26-000002-index.htm",
        ["99.1"],
    )
    assert matches == [
        {
            "exhibit_number": "99.1",
            "document_name": "amzn-20251231xex991.htm",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000002/amzn-20251231xex991.htm",
        }
    ]
