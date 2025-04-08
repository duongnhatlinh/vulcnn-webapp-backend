import os
import subprocess
import tempfile
import glob
import shutil

def run_joern_analysis(file_path):
    """
    Run Joern analysis on a C/C++ file and extract data for PDG generation
    
    Args:
        file_path (str): Path to the C/C++ file
        
    Returns:
        str: Path to generated DOT file or None if failed
    """
    try:
        # Create temporary working directory
        temp_dir = tempfile.mkdtemp()
        bin_dir = os.path.join(temp_dir, 'bin')
        os.makedirs(bin_dir, exist_ok=True)
        
        # Get the base filename without extension
        file_name = os.path.basename(file_path).split('.')[0]
        bin_file = os.path.join(bin_dir, f"{file_name}.bin")
        
        # Step 1: Parse file with Joern to generate .bin file
        print(f"Parsing file {file_path} to {bin_file}")
        process = subprocess.run(
            ['joern-parse', file_path, '--language', 'c', '--output', bin_file],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if parsing was successful
        if process.returncode != 0:
            print(f"Joern parse error: {process.stderr}")
            return None
        
        # Check if bin file was created
        if not os.path.exists(bin_file):
            print(f"Bin file not created at {bin_file}")
            return None
            
        # Step 2: Export PDG from the bin file
        pdg_out_dir = os.path.join(temp_dir, 'pdg_out')
        os.makedirs(pdg_out_dir, exist_ok=True)
        
        pdg_out = os.path.join(pdg_out_dir, file_name)
        
        print(f"Exporting PDG from {bin_file} to {pdg_out}")
        export_process = subprocess.run(
            ['joern-export', bin_file, '--repr', 'pdg', '--out', pdg_out],
            capture_output=True,
            text=True
        )
        
        # Check if export was successful
        if export_process.returncode != 0:
            print(f"Joern export error: {export_process.stderr}")
            return None
            
        # Find the generated PDG file (should be named something like 1-pdg.dot)
        try:
            # Look specifically for the "0-pdg.dot" file
            pdg_file = os.path.join(pdg_out, "1-pdg.dot")
            
            # Check if the file exists
            if not os.path.exists(pdg_file):
                print(f"File 1-pdg.dot not found in {pdg_out}")
                return None
            
            # Return the path to the PDG file
            return pdg_file
                    
        except Exception as e:
            print(f"Error finding PDG file: {str(e)}")
            return None
        
    except Exception as e:
        print(f"Error in Joern analysis: {str(e)}")
        return None
    
    finally:
        # We don't clean up the temporary directory here
        # because we need to return the path to the PDG file
        # The caller is responsible for copying the PDG file
        # to a permanent location and then cleaning up
        pass