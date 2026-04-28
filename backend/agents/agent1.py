import logging
from typing import Dict, Any

logger = logging.getLogger("agent1")

# ✅ TARGET_RSIDS for Early-Exit Stream Parsing
TARGET_RSIDS = {"rs3892097", "rs1065852", "rs12248560", "rs4244285", "rs2740574"}

# ✅ Hospital-Grade Coordinate Map (GRCh38)
VARIANT_MAP = {
    'rs3892097': {'enzyme': 'CYP2D6', 'phenotype': 'Poor Metabolizer', 'chrom': '22', 'pos': 42127941},
    'rs1065852': {'enzyme': 'CYP2D6', 'phenotype': 'Intermediate Metabolizer', 'chrom': '22', 'pos': 42128945},
    'rs12248560': {'enzyme': 'CYP2C19', 'phenotype': 'Ultra-Rapid Metabolizer', 'chrom': '10', 'pos': 94762706},
    'rs4244285': {'enzyme': 'CYP2C19', 'phenotype': 'Poor Metabolizer', 'chrom': '10', 'pos': 94775106},
    'rs2740574': {'enzyme': 'CYP3A4', 'phenotype': 'Intermediate Metabolizer', 'chrom': '7', 'pos': 99781111}
}

async def extract_enzyme_profile(vcf_source: Any) -> Dict[str, str]:
    """
    Agent 1: Bio-Sequencer (Diagnostic Mode)
    - Greedy string matching + Strict Column Mapping.
    - Diagnostic logging for every critical step.
    - Early-exit once all target variants are found.
    """
    profile = {
        "CYP2D6": "Insufficient Data",
        "CYP2C19": "Insufficient Data",
        "CYP3A4": "Insufficient Data"
    }

    if not vcf_source:
        logger.warning("LOG: No VCF source provided.")
        return profile

    logger.info("LOG: Starting VCF scan...")
    found_rsids = set()
    found_variants = []
    line_count = 0
    
    try:
        # Determine if we are reading from a path or a file-like object
        if isinstance(vcf_source, str):
            logger.info(f"LOG: Opening file {vcf_source}...")
            f = open(vcf_source, "r")
        else:
            logger.info("LOG: Reading from upload stream...")
            f = vcf_source

        # Hunting Logic
        for line in f:
            line_count += 1
            # Handle byte streams if necessary
            if isinstance(line, bytes):
                line = line.decode("utf-8")

            if line.startswith("#"):
                continue

            # Diagnostic Log: Show progress every 10,000 lines or for first 10 lines
            if line_count <= 5 or line_count % 10000 == 0:
                logger.info(f"LOG: Scanning line {line_count}: {line[:50].strip()}...")

            # 1. Greedy Line Search: Check if any target rsID exists in the string
            found_any_target = False
            matched_rsid = None
            for rsid in TARGET_RSIDS:
                if rsid in line:
                    found_any_target = True
                    matched_rsid = rsid
                    break
            
            if found_any_target:
                # 2. Strict Column Mapping: Split by tabs and spaces
                parts = line.replace(" ", "\t").split("\t")
                parts = [p for p in parts if p.strip()] # Remove empty strings from double separators

                if len(parts) >= 5:
                    variant_id = parts[2]
                    alt_allele = parts[4]

                    if variant_id == matched_rsid:
                        logger.info(f"LOG: MATCH FOUND! rsID {variant_id} detected in column 3.")
                        
                        # 3. Mutation Check: Ensure ALT is not '.'
                        if alt_allele != "." and alt_allele != "":
                            logger.info(f"LOG: ALT allele is {alt_allele}. Mapping to phenotype...")
                            target = VARIANT_MAP[variant_id]
                            found_variants.append((target['enzyme'], target['phenotype']))
                            found_rsids.add(variant_id)
                        else:
                            logger.warning(f"LOG: rsID {variant_id} found but ALT allele is missing/reference.")

            # ✅ EARLY EXIT: Stop reading if all targets are found
            if len(found_rsids) == len(TARGET_RSIDS):
                logger.info(f"LOG: Early Exit at line {line_count}. All target variants found.")
                break

        if isinstance(vcf_source, str):
            f.close()

        # Phenotype Mapping
        impact_order = {
            "Poor Metabolizer": 4, 
            "Ultra-Rapid Metabolizer": 3, 
            "Intermediate Metabolizer": 2, 
            "Normal": 1, 
            "Insufficient Data": 0
        }

        for enzyme, phenotype in found_variants:
            current_val = profile[enzyme]
            if impact_order.get(phenotype, 0) > impact_order.get(current_val, 0):
                profile[enzyme] = phenotype

        logger.info(f"LOG: Final Enzyme Profile before exit: {profile}")
        return profile

    except Exception as e:
        logger.error(f"LOG: Diagnostic Parsing Error at line {line_count}: {e}")
        return profile