
def refresh_highlightingview(doc):
    # Construct highlighting view
    highlightingview = []
    for i in range(len(doc.view.text)):
        opos = doc.view.vpos_to_opos[i]
        if opos in doc.highlighting:
            highlightingview.append(doc.highlighting[opos])
        else:
            highlightingview.append('')
    doc.view.highlighting = highlightingview

