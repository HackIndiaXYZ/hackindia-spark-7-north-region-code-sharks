import pytest
import os
import json
from src.agents.bio_sequencer import BioSequencer

def test_bio_sequencer_mock_vcf():
    vcf_path = os.path.join("data", "mock_variants.vcf")
    # Ensure mock VCF exists
    assert os.path.exists(vcf_path)
    
    sequencer = BioSequencer(vcf_path)
    profile = sequencer.generate_enzyme_profile()
    
    # Expected results based on mock_variants.vcf:
    # chr22 42127941 rs3892097 C T -> GT 1/1 (CYP2D6 Poor)
    # chr10 94762731 rs4244285 G A -> GT 0/1 (CYP2C19 Intermediate)
    # chr7 99756914 rs35599367 C T -> GT 0/0 (CYP3A4 Normal)
    
    assert profile["CYP2D6"] == "Poor Metabolizer"
    assert profile["CYP2C19"] == "Intermediate Metabolizer"
    assert profile["CYP3A4"] == "Normal Metabolizer"

def test_bio_sequencer_missing_vcf():
    with pytest.raises(FileNotFoundError):
        BioSequencer("non_existent.vcf")

def test_bio_sequencer_insufficient_data():
    # Create a VCF with no matching rsIDs
    vcf_content = """##fileformat=VCFv4.2
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chr1	123	rs1	A	G	100	PASS	.	GT	0/0
"""
    temp_vcf = "data/temp_empty.vcf"
    with open(temp_vcf, "w") as f:
        f.write(vcf_content)
    
    sequencer = BioSequencer(temp_vcf)
    profile = sequencer.generate_enzyme_profile()
    
    assert profile["CYP2D6"] == "Insufficient Genomic Data"
    
    os.remove(temp_vcf)
