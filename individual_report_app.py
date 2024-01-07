import streamlit as st
import pandas as pd
from circular_matrix import plot_matrix, get_suggestion
from clustering_test import cluster_assignment, clusters
from comparing_similarities import get_percentiles_for_business
from clustering_test import clustering_model
from dotenv import load_dotenv
import pinecone
import os
from processing_reasoning_module import get_processing_reason

load_dotenv()
pinecone.init(api_key=os.environ.get("PINECONE_API_KEY"), environment='us-west4-gcp-free')
index_name = 'green'
index = pinecone.Index(index_name)


df = pd.read_json('outputs/combined_data_first_200_rows.jsonl', lines=True)
strat_descriptions = {"RPO":"Retain Product Ownership: Producer rents or leases rather than selling the product.",
                      "DFR":"Design for Recycling: The company redesigns the product or its manufacturing and related processes to maximize recoverability of the materials involved.",
                      "PLE": "Product Life Extension: The company produces its product to last longer either by design or by providing related services.",
                      "PARTNERSHIP": "Partnering specific technological expertise or organizations to increase efficiency and reduce wastage"
                      }
strat_full_names = {"RPO": "RPO (Retain Product Ownership)",
                    "DFR": "DFR (Design for Recycling)",
                    "PLE": "PLE (Product Life Extension)",
                    "PARTNERSHIP": "PARTNERSHIP"}


def report(id):
     business = df[df['id']==id].iloc[0]
     st.title(business['product'])
     st.header("Problem Statement")
     st.write(business['problem'])
     st.header("Solution")
     st.write(business['summary'])
     with st.expander("More Detailed Description"):
          st.write(business['solution'])
     # columns = st.columns(3)
     percentiles = get_percentiles_for_business(id, df, cluster_assignment, clustering_model, index)
     st.subheader("Processing Level")
     st.write(f"How hard is it to process the relevant materials for this {business['product']}?")
     st.write(round(business['processing_level'],2))
     st.write(f"This business is at the {round(percentiles['business_processing_percentile'],2)}th percentile of similar businesses")
     with st.expander("See reasoning"):
          st.write((get_processing_reason(business['problem'], business['solution'], business['processing_level']).processing_reasoning))
     st.subheader("Access Level")
     st.write(f"How hard is it to retrieve the relevant materials for this {business['product']}?")
     st.write(round(business['access_level'],2))
     st.write(f"This business is at the {round(percentiles['business_access_percentile'],2)}th percentile of similar businesses")
     st.subheader("Embedded Value Rating")
     st.write(f"How much value do the relevant materials contain for {business['product']}?")
     st.write(round(business['embedded_value'],2))
     st.write(f"This business is at the {round(percentiles['business_embedded_percentile'],2)}th percentile of similar businesses")
     st.subheader("Business Strategies Deployed:")
     for c in business['categories']:
          with st.expander(strat_full_names[c]):
               st.write(strat_descriptions[c])
     st.subheader(f"How does the {business['product']} business compare with similar businesses in the Circular Economy? - The Circular Matrix")
     similar_businesses = df[df['id'].isin(clusters[cluster_assignment[id]])]
     st.write(plot_matrix(similar_businesses, business['processing_level'], business['access_level']))
     st.header("Recommended Business Strategy")
     suggested = get_suggestion(business['processing_level'], business['access_level'], business['embedded_value'])
     for c in suggested:
          if c in business['categories']:
               with st.expander(f"{c}: Already deployed!"):
                    st.write(strat_descriptions[c])
          else:
               with st.expander(f"{c}: Not yet deployed"):
                    st.write(strat_descriptions[c])

if __name__ == "__main__":
     report(1)