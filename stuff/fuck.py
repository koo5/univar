
import subprocess
gv_output_file_name = "./visualizations/kbdbgtests_agda_listform_tau_1.n3/kbdbgtests_agda_listform_tau_1.n3_00075.gv"
try:
	subprocess.check_output( ("convert", '-regard-warnings', "-extent", '6000x3000',  gv_output_file_name,  '-gravity', 'NorthWest', '-background', 'white', gv_output_file_name + '.svg'))
except subprocess.CalledProcessError as e:
	print('eee', e.output, e.stderr)
	raise


