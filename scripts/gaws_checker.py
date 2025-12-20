import os
import sys
import re

def check_approval(phase_name=None):
    """
    Reviewer Agent による APPROVED が存在するか確認する。
    """
    report_path = 'docs/reports/reviewer_report_final.md' # または個別の報告書
    if not os.path.exists(report_path):
        report_path = 'docs/reports/reviewer_report.md'
    
    if not os.path.exists(report_path):
        print(f"❌ Error: Reviewer report not found at {report_path}")
        return False

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "APPROVED" not in content:
        print(f"❌ Error: APPROVED status not found in {report_path}")
        return False
    
    print(f"✅ Success: APPROVED status confirmed in {report_path}")
    return True

def check_impact_analysis():
    """
    Impact Analysis が実施されているか確認する。
    """
    report_path = 'docs/reports/impact_analysis_report.md'
    if not os.path.exists(report_path):
        print(f"❌ Error: Impact Analysis report not found at {report_path}")
        return False
    
    print(f"✅ Success: Impact Analysis confirmed.")
    return True

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "merge"
    
    if mode == "merge":
        if not check_approval():
            sys.exit(1)
    elif mode == "feature_start":
        if not check_impact_analysis():
            sys.exit(1)
    
    print("🚀 All workflow guards passed.")
    sys.exit(0)
