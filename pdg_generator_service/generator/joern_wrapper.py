import os
import subprocess
import tempfile
import json
import shutil

def run_joern_analysis(file_path):
    """
    Run Joern analysis on a C/C++ file and extract data for PDG generation
    
    Args:
        file_path (str): Path to the C/C++ file
        
    Returns:
        dict: Joern analysis result or None if failed
    """
    try:
        # Create temporary working directory
        temp_dir = tempfile.mkdtemp()
        bin_dir = os.path.join(temp_dir, 'bin')
        os.makedirs(bin_dir, exist_ok=True)
        
        # Step 1: Parse file with Joern
        process = subprocess.run(
            ['joern-parse', file_path, '--output', bin_dir],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if parsing was successful
        if process.returncode != 0:
            print(f"Joern parse error: {process.stderr}")
            return None
        
        # Find generated CPG (Code Property Graph)
        bin_files = os.listdir(bin_dir)
        if not bin_files:
            print("No CPG files generated")
            return None
        
        cpg_path = os.path.join(bin_dir, bin_files[0])
        
        # Step 2: Export PDG data
        script_path = os.path.join(os.path.dirname(__file__), 'export_pdg.sc')
        if not os.path.exists(script_path):
            # Create script file if it doesn't exist
            with open(script_path, 'w') as f:
                f.write("""
                @main def main(cpgFile: String) = {
                  importCpg(cpgFile)
                  val methods = cpg.method.internal.l
                  
                  val pdgData = methods.map { method =>
                    val name = method.name
                    val pdgEdges = method.cpg.pdg.edges.l
                    val nodes = method.cpg.pdg.vertices.l
                                        
                    (name, nodes, pdgEdges)
                  }
                  
                  println(pdgData.toJson)
                  println("PDG_EXPORT_COMPLETE")
                }
                """)
        
        # Run Joern script to export PDG data
        process = subprocess.run(
            ['joern', '--script', script_path, '--params', f'cpgFile={cpg_path}'],
            capture_output=True,
            text=True
        )
        
        # Extract PDG data from output
        output = process.stdout
        if "PDG_EXPORT_COMPLETE" not in output:
            print(f"Joern script error: {process.stderr}")
            return None
        
        # Parse JSON output
        json_data = output.split("PDG_EXPORT_COMPLETE")[0].strip()
        result = json.loads(json_data)
        
        return result
    
    except Exception as e:
        print(f"Error in Joern analysis: {str(e)}")
        return None
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)