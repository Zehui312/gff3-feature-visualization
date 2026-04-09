from dna_features_viewer import GraphicFeature, GraphicRecord
import gffutils
import pandas as pd

import os   
import argparse


parser = argparse.ArgumentParser(description="Plot genome features from GFF3 file.")
parser.add_argument("--gff_path", required=True, help="Path to the GFF3 file.")
parser.add_argument("--start", type=int, required=True, help="Start position of the region to plot.")
parser.add_argument("--end", type=int, required=True, help="End position of the region to plot.")
parser.add_argument("--contig_num", required=True, help="Contig number to select.")
parser.add_argument("--length_per_line", type=int, default=10000, help="Nucleotides per line in plot.")
parser.add_argument("--lines_per_page", type=int, default=5, help="Lines per page in plot.")
parser.add_argument("--output_name", required=False, help="Path to save the output plot.")
args = parser.parse_args()

gff_path = args.gff_path
contig_num = args.contig_num
start = args.start
end = args.end
length_line = args.length_per_line
lines_page = args.lines_per_page
output_name = args.output_name
print(">>>>>>>>>>>>>>>The parameters you provided<<<<<<<<<<<<<<<")
print("GFF3 file path:", gff_path)
print("Contig number:", contig_num)
print("Start position:", start)
print("End position:", end)
print("Nucleotides per line:", length_line)
print("Lines per page:", lines_page)
print("Output plot path:", args.output_name)
#%%
#=================================================================
#++++++++++++++++++++Step 1 gff3 file import ++++++++++++++++++++
#================================================================= 
db = gffutils.create_db(gff_path, dbfn=":memory:", force=True, keep_order=True, merge_strategy="merge", sort_attribute_values=True)
features_type = ["CDS", "CRISPR", "crispr-repeat", "crispr-spacer","ncRNA","oriC","oriT" ,"regulatory_region","rRNA", "tRNA","tmRNA"]

records = []
for feat in db.features_of_type(features_type):
    records.append({
        "id": feat.id,
        "seqid": feat.chrom,
        "featuretype": feat.featuretype,
        "start": feat.start,
        "end": feat.end,
        "strand": feat.strand,
        "attributes_gene": feat.attributes.get("gene", [""])[0],
        "attributes_Name": feat.attributes.get("Name", [""])[0]
    })

# Turn into DataFrame
df = pd.DataFrame(records)
df.loc[df["attributes_Name"].str.contains("transposase", case=False, na=False), "featuretype"] = "tnp"
Chr_select = df[df["seqid"] == contig_num]
Chr_select_loc = Chr_select[(Chr_select["start"] >= start) & (Chr_select["start"] <= end)]


print("================================")
print("Selected contig:", contig_num)
print(Chr_select_loc["featuretype"].unique())
print("================================")

#=================================================================
#++++++++++++++++++++Step 2 Assignment the color ++++++++++++++++++
#=================================================================

color_dict_featuretype = {
    "CDS": "#c4c5c6",
    "CRISPR": "#ffffcc",
    "crispr-repeat": "#ffffcc",
    "crispr-spacer": "#ffffcc",
    "ncRNA": "#ccffcc",
    "oriC": "#ccccff",
    "oriT": "#ccccff",
    "regulatory_region": "#ccccff",
    "rRNA": "#ccffff",
    "tRNA": "#ccffff",
    "tmRNA": "#ccffff",
    "tnp": "#d35230",
}

features = []
for idx, row in Chr_select_loc.iterrows():
    features.append(
        GraphicFeature(
            start=row["start"],
            end=row["end"],
            strand=+1 if row["strand"] == "+" else -1 if row["strand"] == "-" else None,
            color=color_dict_featuretype.get(row["featuretype"], "#FFFFFF"),
            label=row["attributes_gene"] if row["attributes_gene"] else row["attributes_Name"]
        )
    )

#%%
#=================================================================
#++++++++++++++++++++Step 3 Plotting the features ++++++++++++
#=================================================================

record = GraphicRecord(sequence_length=Chr_select["end"].max(), features=features)
subrecord = record.crop((start, end))
subrecord.plot_on_multiple_pages(
    f"{output_name}.pdf",
    nucl_per_line=length_line,
    lines_per_page=lines_page,
    plot_sequence=False
)


