import subprocess
import os
import pandas as pd

class Visualizer:
    def __init__(self, args, rpkm_heater_path, stats_dir_path):
        self.args = args
        self.rpkm_heater_path = rpkm_heater_path
        self.stats_dir_path = stats_dir_path

    def visualize(self):
        self.plot_heatmaps()

    def plot_heatmaps(self):
        # make appropriate dir
        rpkm_output_dir = self.create_rpkm_output_dir()

        sort_gen_addon = ""
        sort_samples_addon = ""

        # incorporate optional sort_gen and sort_sample options for rpkm_heater
        if self.args.sort_gen:
            sort_gen_addon = "-sort_gen {0}".format(self.args.sort_gen)
        if self.args.sort_samples:
            sort_samples_addon = "-sort_samples {0}".format(self.args.sort_samples)

        cmd = "rpkm_heater -map -i {1} -o {2} -project {3} {4} {5}".format(self.rpkm_heater_path,
                                                                           self.stats_dir_path,
                                                                           rpkm_output_dir,
                                                                           self.args.n,
                                                                           sort_gen_addon,
                                                                           sort_samples_addon)
        if self.args.verbosity:
            print("running: " + cmd)

        subprocess.run(cmd, shell=True)

    def calculate_rpkm(self):
        # make appropriate dir
        rpkm_output_dir = self.create_rpkm_output_dir()

        # df holds rpkm values with genome acc as the row names and metaG acc as the headers
        df = pd.DataFrame()

        # loop through files with bam.stats suffix in generated stats dir
        for file in os.listdir(self.stats_dir_path):
            if file.endswith(".bam.stats"):

                # rpkm dict will hold rpkm values for single metaG
                rpkm = {}
                # read csv
                entry = pd.read_csv(os.path.join(self.stats_dir_path, file), delimiter="\t", header=None)
                # add headers to pd
                entry.columns = ["genome", "gen_length", "r_mapped", "r_unmapped"]
                # calculate total mapped reads
                tot_reads = entry['r_mapped'].sum()

                # specify metaG accession in dict
                rpkm['ACC'] = [file[:-10]]

                # specify rpkm values for each genome for this specific metaG
                for i in range(len(entry['genome'])):
                    if entry['genome'][i] != "*":
                        rpkm[entry['genome'][i]] = \
                            [entry['r_mapped'][i]/((entry['gen_length'][i]/1000)*(tot_reads/1000000))]

                # convert dict to data frame and transpose
                rpkm_df = pd.DataFrame(rpkm)
                rpkm_df.set_index('ACC', inplace=True)
                rpkm_df = rpkm_df.transpose()

                # add rpkm data to overall dataframe
                df = pd.concat([df, rpkm_df], axis=1, join='outer')

        if self.args.verbosity:
            print(df, "\n")
        df.to_csv(os.path.join(rpkm_output_dir, self.args.n + "_rpkm_noLog.csv"), index_label='ACC')

    def create_rpkm_output_dir(self):
        # make appropriate dir
        rpkm_base_dir = os.path.join(self.args.o, "rpkm")
        rpkm_output_dir = os.path.join(rpkm_base_dir, self.args.n)

        if not os.path.isdir(rpkm_base_dir):
            subprocess.run("mkdir {}".format(rpkm_base_dir), shell=True)
        if not os.path.isdir(rpkm_output_dir):  
            subprocess.run("mkdir {}".format(rpkm_output_dir), shell=True)
        
        return rpkm_output_dir

