#!/usr/bin/env python3

import os
import sys


def setup_fasta(dada_csv_file,fasta_output_file):
	csv_lines = []
	firstlineflag = 1
	fasta_print = ''
	with open(dada_csv_file) as f:
		for line in f:
			line = line.rstrip('\n')
			if firstlineflag==1:
				firstlineflag = 0
				header = line
			else:
				splitline = line.split(";")
				csv_lines.append(splitline)
				seq_number = splitline[0][1:-1]
				seq = splitline[1][1:-1]
				asv_name = splitline[2]
				fasta_print += '>'+seq_number+'\n'+seq+'\n'
	o = open(fasta_output_file,'w')
	o.write(fasta_print)
	o.close()
	return(header, csv_lines)

def run_blast(ASV_fasta,reference_fasta,blast_output_file):
	cmd = 'blastn -query '+ASV_fasta+' -subject '+reference_fasta+' -out '+blast_output_file+' -outfmt 6 -perc_identity 100'
	os.system(cmd)

def parse_blast(blast_output_file):
	ASV_to_ref = {}
	bitscores = {}
	with open(blast_output_file) as f:
		for line in f:
			line = line.rstrip('\n').split('\t')
			pident = float(line[2])
			if pident == 100:
				ASV_number = line[0]
				ref_number = line[1]
				bitscore = float(line[11])
				if ASV_number in ASV_to_ref:
					if bitscores[ASV_number]<bitscore:
						ASV_to_ref[ASV_number] = ref_number
						bitscores[ASV_number] = bitscore
				else:
					ASV_to_ref[ASV_number] = ref_number
					bitscores[ASV_number] = bitscore
	return(ASV_to_ref)

def rename_ASVs(ASV_to_ref_dict,csv_header,csv_lines,dada_csv_renamed_file):
	printline = csv_header+'\n'
	for line in csv_lines:
		ASV_number = line[0][1:-1]
		if ASV_number in ASV_to_ref_dict:
			new_ASV_number = "\"seq"+ASV_to_ref_dict[ASV_number]+"\""
			old_ASV_number = line[2]
			if new_ASV_number != old_ASV_number:
				print(old_ASV_number+' renamed to '+new_ASV_number, file=sys.stderr)
				line[2] = new_ASV_number
		printline += ';'.join(line)+'\n'
	o = open(dada_csv_renamed_file,'w')
	o.write(printline)
	o.close()



dada_csv_file = sys.argv[1]
fasta_output_file = sys.argv[2]
reference_fasta = sys.argv[3]
blast_output_file = sys.argv[4]
new_dada_file = sys.argv[5]

csv_header, csv_lines = setup_fasta(dada_csv_file,sys.argv[2])

if not os.path.exists(blast_output_file):
	run_blast(fasta_output_file,reference_fasta,blast_output_file)
ASV_to_ref_dict = parse_blast(blast_output_file)
rename_ASVs(ASV_to_ref_dict,csv_header,csv_lines,new_dada_file)