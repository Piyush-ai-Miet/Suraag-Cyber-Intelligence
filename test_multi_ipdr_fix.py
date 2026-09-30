"""
Test script to verify multiple IPDR file loading without duplicate column errors
"""
import pandas as pd
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.ipdr_analyzer import load_and_validate, add_uppercase_aliases

def test_multiple_files():
    """Test loading and concatenating multiple IPDR files"""
    
    print("=" * 60)
    print("Testing Multiple IPDR File Loading")
    print("=" * 60)
    
    # Test files
    file1_path = "data/sample_ipdr.csv"
    file2_path = "data/realistic_ipdr_sample.csv"
    
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        print("❌ Test files not found")
        return False
    
    # Load file 1
    print(f"\n1️⃣ Loading {file1_path}...")
    with open(file1_path, 'rb') as f:
        df1, error1 = load_and_validate(f.read(), file1_path)
    
    if error1:
        print(f"❌ Error loading file 1: {error1}")
        return False
    
    print(f"✅ File 1 loaded: {len(df1)} rows, {len(df1.columns)} columns")
    print(f"   Columns: {sorted(df1.columns.tolist()[:10])}...")
    
    # Load file 2
    print(f"\n2️⃣ Loading {file2_path}...")
    with open(file2_path, 'rb') as f:
        df2, error2 = load_and_validate(f.read(), file2_path)
    
    if error2:
        print(f"❌ Error loading file 2: {error2}")
        return False
    
    print(f"✅ File 2 loaded: {len(df2)} rows, {len(df2.columns)} columns")
    print(f"   Columns: {sorted(df2.columns.tolist()[:10])}...")
    
    # Add suspect labels
    df1['_suspect_label'] = 'Suspect_A'
    df1['_file_name'] = 'File1'
    df2['_suspect_label'] = 'Suspect_B'
    df2['_file_name'] = 'File2'
    
    # Concatenate
    print(f"\n3️⃣ Concatenating dataframes...")
    try:
        combined_df = pd.concat([df1, df2], ignore_index=True)
        print(f"✅ Concatenation successful: {len(combined_df)} rows")
    except Exception as e:
        print(f"❌ Concatenation failed: {e}")
        return False
    
    # Check for duplicate columns
    print(f"\n4️⃣ Checking for duplicate columns...")
    duplicate_cols = combined_df.columns[combined_df.columns.duplicated()].tolist()
    if duplicate_cols:
        print(f"❌ Found duplicate columns: {duplicate_cols}")
        return False
    else:
        print(f"✅ No duplicate columns found")
    
    # Add uppercase aliases
    print(f"\n5️⃣ Adding uppercase aliases...")
    try:
        combined_df = add_uppercase_aliases(combined_df)
        print(f"✅ Aliases added successfully: {len(combined_df.columns)} total columns")
    except Exception as e:
        print(f"❌ Failed to add aliases: {e}")
        return False
    
    # Verify required columns exist
    print(f"\n6️⃣ Verifying required columns...")
    required_cols = ['Source_IP', 'Destination_IP', 'Timestamp', 'Subscriber_Name']
    missing_cols = [col for col in required_cols if col not in combined_df.columns]
    
    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        return False
    else:
        print(f"✅ All required columns present")
    
    # Check data integrity
    print(f"\n7️⃣ Checking data integrity...")
    suspect_a_count = len(combined_df[combined_df['_suspect_label'] == 'Suspect_A'])
    suspect_b_count = len(combined_df[combined_df['_suspect_label'] == 'Suspect_B'])
    
    print(f"   Suspect_A records: {suspect_a_count}")
    print(f"   Suspect_B records: {suspect_b_count}")
    
    if suspect_a_count != len(df1) or suspect_b_count != len(df2):
        print(f"❌ Data integrity check failed")
        return False
    else:
        print(f"✅ Data integrity verified")
    
    # Final summary
    print(f"\n" + "=" * 60)
    print(f"✅ ALL TESTS PASSED")
    print(f"=" * 60)
    print(f"Combined DataFrame:")
    print(f"  - Total rows: {len(combined_df)}")
    print(f"  - Total columns: {len(combined_df.columns)}")
    print(f"  - Suspects: 2 (Suspect_A, Suspect_B)")
    print(f"  - Date range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
    
    return True


if __name__ == "__main__":
    success = test_multiple_files()
    sys.exit(0 if success else 1)
