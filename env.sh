#/bin/bash
DEEPRACER_DIR=/home/deepracer/DeepPicar-DeepRacer

dr_run_kb()
{
	pushd $DEEPRACER_DIR
	if [ $# -eq 1 ] && [ $1 != "" ]; then
		THR="-t $1"
	else
		THR=""
	fi

	sudo nice --20 python3 deeppicar.py $THR
	popd
}

dr_run_gp()
{
	pushd $DEEPRACER_DIR
	if [ $# -eq 1 ] && [ $1 != "" ]; then
		THR="-t $1"
	else
		THR=""
	fi

	sudo nice --20 python3 deeppicar.py -g $THR
	popd
}

dr_calib_throttle()
{
	pushd $DEEPRACER_DIR
	sudo nice --20 python3 actuator-servo-deepracer.py calib_throttle
	popd
}

dr_calib_steering()
{
	pushd $DEEPRACER_DIR
	sudo nice --20 python3 actuator-servo-deepracer.py calib_steering
	popd
}
