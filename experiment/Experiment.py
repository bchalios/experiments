import os
import sys

from jobs import job

class Experiment:
    def __init__(self, exec_path, arguments, repetitions, res_dir, experiment_name, machine):
        self.__exec_path = exec_path
        self.__res_dir = res_dir
        self.__machine = machine
        self.__repetitions = repetitions
        assert machine in ["mn4", "nord3"], "Unknown machine"
        if machine == "mn4":
            self.__job_scheduler = "slurm"
        elif machine == "nord3":
            self.__job_scheduler = "lsf"

        #create runscript name
        self.__runscript = "runscripts/{0}_{1}.sh".format(self.__job_scheduler, experiment_name)
        self._job = job.job(self.__runscript, self.__job_scheduler)
        self._job.set_command(self.__exec_path, self.__repetitions)
        self._job.set_args(arguments)
        self._job.set_jobname(experiment_name)
        self._debug_job = False

        #nanos6-development module is useful for all benchmarks that use liberep
        #on MN4 gcc/7.2.0 is a requirement for liberep to work
        self._modules_load = ['gcc/7.2.0', 'nanos6-development', 'intel', 'mkl', 'impi']
        self._modules_unload = ['openmpi', 'nanos6-development']

        #Create all needed directories if not there
        try:
            os.makedirs(self.__res_dir)
        except OSError:
            if not os.path.isdir(self.__res_dir):
                raise

        #create runscripts folder if it's not present
        try:
            os.makedirs('runscripts')
        except OSError:
            if not os.path.isdir('runscripts'):
                raise
        
    def set_nrtasks(self, nrtasks):
        self._job.set_nrtasks(nrtasks)

    def set_nrnodes(self, nrnodes):
        self._job.set_nrnodes(nrnodes)

    def set_cpus_per_task(self, cpus_per_task):
        self._job.set_cpus_per_task(cpus_per_task)

    def set_stdout(self, stdout):
        truncate = (self.__repetitions == 1)
        self._job.set_stdout(stdout, truncate)

    def set_stderr(self, stderr):
        truncate = (self.__repetitions == 1)
        self._job.set_stderr(stderr, truncate)

    def set_job_minutes(self, minutes):
        self._job.set_timelimit(0, minutes)

    def set_debug_job(self, is_debug):
        if is_debug:
            self._job.set_queue('debug')

    def enable_extrae(self, lib="libptmpitrace", config="extrae.xml", prog_name="extrae", tmp_dir=".", final_dir=".", extrae_module="EXTRAE/3.5.2"):
        self._modules_load.append(extrae_module)
        self._modules_unload.append("extrae")
        self._job.set_envar('LD_PRELOAD', "${{EXTRAE_HOME}}/lib/{0}.so".format(lib))
        self._job.set_envar('EXTRAE_CONFIG_FILE', config)
        self._job.set_envar('EXTRAE_PROGRAM_NAME', prog_name)
        self._job.set_envar('EXTRAE_FINAL_DIR', final_dir)
        self._job.set_envar('EXTRAE_DIR', tmp_dir)
        self._job.set_envar('NANOS6_EXTRAE_AS_THREADS', 1)

class ExperimentClusters(Experiment):
    def __init__(self, exec_path, arguments, repetitions, res_dir, experiment_name, machine="mn4"):
        Experiment.__init__(self, exec_path, arguments, repetitions, res_dir, experiment_name, machine)
        self._modules_load.append('nanos6')
        self._modules_unload.append('nanos6')
        self._modules_unload.append('ompss')
        self._job.set_envar("NANOS6", "optimized")
        self._job.set_envar("NANOS6_SCHEDULER", "cluster-random")
        self._job.set_envar("NANOS6_COMMUNICATION", "mpi-2sided")
        self._job.set_envar("NANOS6_CPU_SCHEDULER", "default")
        self._job.set_envar("NANOS6_DISTRIBUTED_MEMORY", "4G")
        self._job.set_envar("NANOS6_LOCAL_MEMORY", "1G")
        self._job.set_envar("NANOS6_VERBOSE", "all,!LeaderThread")
        self._job.set_envar("NANOS6_COMMUNICATION", "mpi-2sided")

    def set_runtime(self, runtime):
        self._job.set_envar("NANOS6", runtime)

    def set_scheduler(self, scheduler):
        self._job.set_envar("NANOS6_SCHEDULER", scheduler)

    def set_cpu_scheduler(self, scheduler):
        self._job.set_envar("NANOS6_CPU_SCHEDULER", scheduler)

    def set_mem_distributed(self, mem):
        self._job.set_envar("NANOS6_DISTRIBUTED_MEMORY", mem)

    def set_mem_local(self, mem):
        self._job.set_envar("NANOS6_LOCAL_MEMORY", mem)

    def set_verbosity(self, verbosity):
        self._job.set_envar("NANOS6_VERBOSE", "all")

    def run_experiment(self):
        self._job.set_modules(self._modules_load, self._modules_unload)
        self._job.submit_job()
        

class ExperimentMPI(Experiment):
    def __init__(self, exec_path, arguments, repetitions, res_dir, experiment_name, machine="mn4"):
        Experiment.__init__(self, exec_path, arguments, repetitions, res_dir, experiment_name, machine)

    def run_experiment(self):
        self._job.set_modules(self._modules_load, self._modules_unload)
        self._job.submit_job()
