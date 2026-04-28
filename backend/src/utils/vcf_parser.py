import pandas as pd
import os

class VCFParser:
    def __init__(self, vcf_path):
        self.vcf_path = vcf_path
        self.variants = self._parse_vcf()

    def _parse_vcf(self):
        """Parses a VCF file and returns a list of variants."""
        if not os.path.exists(self.vcf_path):
            raise FileNotFoundError(f"VCF file not found: {self.vcf_path}")
        
        records = []
        header = []
        with open(self.vcf_path, 'r') as f:
            for line in f:
                if line.startswith('##'):
                    continue
                if line.startswith('#'):
                    header = line.lstrip('#').strip().split('\t')
                    continue
                
                if not header:
                    continue # Should not happen in a valid VCF
                    
                values = line.strip().split('\t')
                record = dict(zip(header, values))
                records.append(record)
        
        if not header:
            return pd.DataFrame() # Return empty DF if no header
            
        return pd.DataFrame(records, columns=header)

    def get_variant_genotype(self, rsid):
        """Returns the genotype (GT) for a given rsID."""
        if self.variants.empty or 'ID' not in self.variants.columns:
            return None
        
        match = self.variants[self.variants['ID'] == rsid]
        if match.empty:
            return None
        
        # In a real VCF, the GT is usually the first field in the SAMPLE column
        # Our mock VCF follows this pattern.
        sample_col = self.variants.columns[-1]
        format_col = match['FORMAT'].values[0]
        sample_data = match[sample_col].values[0]
        
        format_fields = format_col.split(':')
        sample_fields = sample_data.split(':')
        
        try:
            gt_index = format_fields.index('GT')
            return sample_fields[gt_index]
        except (ValueError, IndexError):
            return None
