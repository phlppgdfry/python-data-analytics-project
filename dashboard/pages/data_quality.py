"""Data-qualitypagina."""

import json

import streamlit as st

from dashboard.shared import get_dashboard_context, load_quality_report, page_intro


context = get_dashboard_context()
if context is None:
    st.stop()

page_intro("Data quality", "Transparantie over wat de pipeline corrigeert, verwijdert en als betrouwbare analyse-data doorlaat.")
report = load_quality_report()
if not report:
    st.warning("Nog geen kwaliteitsrapport gevonden. Run: python src/run_pipeline.py")
    st.stop()

metrics = st.columns(4)
metrics[0].metric("Raw rows", f"{report['raw_rows']:,}", help="Rijen zoals ze uit de bron komen, vóór cleaning.")
metrics[1].metric("Clean rows", f"{report['clean_rows']:,}", help="Rijen die het Pandera-datacontract doorstaan.")
metrics[2].metric("Removed rows", f"{report['removed_rows']:,}", help="Ongeldige of dubbele bronrijen.")
metrics[3].metric("Retention", f"{report['retention_percent']:.2f}%")

st.subheader("Data contract")
st.markdown(
    """
    Pandera valideert vóór een rij in het dashboard komt:

    - verplichte kolommen en unieke order-ID's;
    - geldige landen en producten;
    - positieve aantallen, prijzen en kostprijzen;
    - kostprijs lager dan verkoopprijs;
    - omzet, brutowinst en marge die correct zijn berekend.
    """
)
st.subheader("Pipeline commands")
st.code("python src/run_pipeline.py --regenerate\npython src/run_pipeline.py --load-postgres", language="bash")
st.caption("The second command requires Docker PostgreSQL to be running. The public Streamlit deployment continues to use its safe CSV fallback.")

with st.expander("View machine-readable quality report"):
    st.json(report)
    st.download_button("Download quality report", json.dumps(report, indent=2).encode("utf-8"), "data_quality_report.json", "application/json", width="content")

with st.expander("Preview cleaned data contract output"):
    st.dataframe(context.filtered_data.head(25), width="stretch", hide_index=True)
