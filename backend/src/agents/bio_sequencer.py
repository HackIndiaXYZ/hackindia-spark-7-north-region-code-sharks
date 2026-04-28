from src.utils.vcf_parser import VCFParser
import json

class BioSequencer:
    """Agent 1: Ingests VCF and extracts specific CYP450 variants."""
    
    # Mapping of Gene -> rsID -> Genotype -> Phenotype
    PHARMACO_MAP = {
        "CYP2D6": {
            "rsid": "rs3892097",
            "phenotypes": {
                "0/0": "Normal Metabolizer",
                "0/1": "Intermediate Metabolizer",
                "1/1": "Poor Metabolizer",
                "1/2": "Intermediate Metabolizer", # Simplification
                "0/2": "Normal Metabolizer"      # Simplification
            }
        },
        "CYP2C19": {
            "rsid": "rs4244285",
            "phenotypes": {
                "0/0": "Normal Metabolizer",
                "0/1": "Intermediate Metabolizer",
                "1/1": "Poor Metabolizer"
            }
        },
        "CYP3A4": {
            "rsid": "rs35599367",
            "phenotypes": {
                "0/0": "Normal Metabolizer",
                "0/1": "Intermediate Metabolizer",
                "1/1": "Poor Metabolizer"
            }
        }
    }

    def __init__(self, vcf_path):
        self.parser = VCFParser(vcf_path)

    def generate_enzyme_profile(self):
        """Generates the patient's Enzyme Profile based on VCF variants."""
        profile = {}
        
        for gene, info in self.PHARMACO_MAP.items():
            rsid = info['rsid']
            gt = self.parser.get_variant_genotype(rsid)
            
            if gt:
                # Normalize genotype (e.g., 1|1 -> 1/1)
                gt = gt.replace('|', '/')
                phenotype = info['phenotypes'].get(gt, "Unknown Metabolizer")
                profile[gene] = phenotype
            else:
                profile[gene] = "Insufficient Genomic Data"
        
        return profile

if __name__ == "__main__":
    # Quick manual test
    import os
    vcf_path = os.path.join("data", "mock_variants.vcf")
    sequencer = BioSequencer(vcf_path)
    profile = sequencer.generate_enzyme_profile()
    print(json.dumps(profile, indent=4))
