#!/bin/bash

show_help() {
cat << EOF
Usage: 
	${0##*/} [-vhapc] [OPERATION] [RESOURCE] [_ADDITIONAL_PARAMS_]
Options:
	v - verbose (vv - more verbose)
	h - help
	a - management api address (could be provided with MANAGEMENT_API_IP env or from config file)
	p - management api port (could be provided with MANAGEMENT_API_PORT env or from config file)
	c - path to config file
Examples: 
	.${0##*/} -a 127.0.0.1 -p 6666 -v create tenant mytenant
	.${0##*/} create e myendpoint mymodel
	.${0##*/} -a 127.0.0.1 login
	.${0##*/} logout
	.${0##*/} run-inference 127.0.0.1 443 numpy imgs.npy 10 mymodel server.crt client.crt client.key
Operations:
	create (c), remove (rm), update (up), scale (s), list (ls), login, logout, upload (u), run-inference (ri)
Resources:
	tenant (t), endpoint (e)
EOF
}

declare -A verbose_dict=( [0]="-s" [1]="" [2]="-v" )
VERBOSE=0
OPTIND=1
DEFAULT_CFG_FILE=~/.inferno
CFG_FILE=${CFG_FILE:=${DEFAULT_CFG_FILE}}

while getopts "hva:p:c:" opt; do
	case $opt in
		h)	show_help
			exit 0
			;;
		v)	let "VERBOSE++"
			echo "Verbose mode selected"
			;;
		a)	MANAGEMENT_API_IP=$OPTARG
			echo "Management api ip: ${MANAGEMENT_API_IP}"
			;;
		p)	MANAGEMENT_API_PORT=$OPTARG
			echo "Management api port: ${MANAGEMENT_API_PORT}"
			;;
		c)  CFG_FILE=$OPTARG
			echo "Config file: ${CFG_FILE}"
			;;
		*)	show_help >&2
			exit 1
			;;
	esac
done
shift "$((OPTIND-1))"

OPERATION=$1
RESOURCE=$2
PARAM_1=$3
PARAM_2=$4
PARAM_3=$5
PARAM_4=$6
PARAM_5=$7

if [[ -s ${CFG_FILE} ]]; then
	TOKEN=`cat ${CFG_FILE} | jq -r '.id_token'`
	[[ -z "${MANAGEMENT_API_IP}" ]] && MANAGEMENT_API_IP=`cat ${CFG_FILE} | jq -r '.management_api_address'`
	[[ -z "${MANAGEMENT_API_PORT}" ]] && MANAGEMENT_API_PORT=`cat ${CFG_FILE} | jq -r '.management_api_port'`
elif [[ ${OPERATION} != "login" ]]; then
	echo "Please login first"
	exit 0
fi

MANAGEMENT_API_IP=${MANAGEMENT_API_IP:-'127.0.0.1'}
MANAGEMENT_API_PORT=${MANAGEMENT_API_PORT:-5000}

CERT=${CERT}
RESOURCES=${RESOURCES:="{\"requests.cpu\": \"1\", \"requests.memory\": \"1Gi\", \"limits.cpu\": \"2\", \"limits.memory\": \"2Gi\", \"maxEndpoints\": 15}"}

case "$OPERATION" in
	create | c) 
		case "$RESOURCE" in
			tenant | t) echo "Create tenant"
				[[ -z ${PARAM_1} ]] && read -p "Please provide tenant name " PARAM_1
				curl ${verbose_dict[$VERBOSE]} -H "accept: application/json" -H "Authorization: $TOKEN" -H "Content-Type: application/json" \
					-d "{\"name\": \"${PARAM_1}\", \"cert\": \"$CERT\", \"scope\":\"scope_name\",\"quota\": ${RESOURCES}}" \
					-X POST "http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants"
				;;
			endpoint | e) echo "Create endpoint"
				[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide model name " PARAM_2
				[[ -z ${PARAM_3} ]] && read -p "Please provide model version " PARAM_3
				[[ -z ${PARAM_4} ]] && read -p "Please provide tenant name " PARAM_4
				curl ${verbose_dict[$VERBOSE]} -X POST \
				"http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants/${PARAM_4}/endpoints" \
				-H "accept: application/json" \
				-H "Authorization: $TOKEN" -H "Content-Type: application/json" \
				-d "{\"modelName\":\"${PARAM_2}\", \"modelVersion\":${PARAM_3}, \"endpointName\":
				\"${PARAM_1}\", \"subjectName\": \"client\", \"resources\": ${RESOURCES}}"
				;;
		esac
		;;
	remove | rm)
		case "$RESOURCE" in
			tenant | t)
				[[ -z ${PARAM_1} ]] && read -p "Please provide tenant name " PARAM_1
				curl  ${verbose_dict[$VERBOSE]}  -H "accept: application/json" -H "Authorization: \
				 $TOKEN" -H "Content-Type: application/json"  \
					-d "{\"name\": \"${PARAM_1}\"}" -X DELETE "http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants"
				;;
			endpoint | e)
				[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide tenant name " PARAM_2
				curl -X DELETE  ${verbose_dict[$VERBOSE]} \
				"http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants/${PARAM_2}/endpoints" -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" -d "{\"endpointName\": \"${PARAM_1}\"}"
				;;
			model | m)
				[[ -z ${PARAM_1} ]] && read -p "Please provide model name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide model version " PARAM_2
				[[ -z ${PARAM_3} ]] && read -p "Please provide tenant name " PARAM_3
				curl -X DELETE  ${verbose_dict[$VERBOSE]} \
				"http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants/${PARAM_3}/models" -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" \
					-d "{\"modelName\": \"${PARAM_1}\", \"modelVersion\": ${PARAM_2}}"
		esac
		;;
	update | up)
		case "$RESOURCE" in
			endpoint | e)
				[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide new model name " PARAM_2
				[[ -z ${PARAM_3} ]] && read -p "Please provide model version " PARAM_3
				[[ -z ${PARAM_4} ]] && read -p "Please provide tenant name " PARAM_4
				curl -X PATCH  ${verbose_dict[$VERBOSE]}  \
				"http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants/${PARAM_4}/endpoints/${PARAM_1}/updating" -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" -d "{\"modelName\": ${PARAM_2}, \"modelVersion\":${PARAM_3}}"
				;;
		esac
		;;
	scale | s)
		case "$RESOURCE" in
			endpoint | e)
				[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide number of replicas " PARAM_2
				[[ -z ${PARAM_3} ]] && read -p "Please provide tenant name " PARAM_3
				curl -X PATCH  ${verbose_dict[$VERBOSE]}  \
				"http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants/${PARAM_3}/endpoints/${PARAM_1}/scaling" -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" -d "{\"replicas\": ${PARAM_2}}"
				;;
		esac
		;;
	login)
		echo "Signing in..."
		if [ -z "${MANAGEMENT_API_IP}" ]; then
			echo "Please provide management api ip address"
			read MANAGEMENT_API_IP
		fi
		python webbrowser_authenticate.py --address ${MANAGEMENT_API_IP} --port ${MANAGEMENT_API_PORT}
		TOKEN=`cat "${CFG_FILE}" | jq -r '.id_token'`
		echo ${TOKEN}
		;;
	logout)
		read -r -p "Are you sure? This will remove all tokens from your config file. [y/n] " response
		if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
			if [ -f ${CFG_FILE} ]; then
				CFG_WITHOUT_TOKENS=`cat ${CFG_FILE} | jq -c '{management_api_address, management_api_port}'`
				echo ${CFG_WITHOUT_TOKENS} > ${CFG_FILE}
				echo "Signed out"
			else
				echo "Config file ${CFG_FILE} does not exist"
			fi
		fi
		;;
	list | ls)	
		case "$RESOURCE" in
			tenant | tenants | t)
				curl -X GET ${verbose_dict[$VERBOSE]} -H "accept: application/json" \
				-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" \
				"http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants"
				;;
			endpoint | endpoints | e)
				[[ -z ${PARAM_1} ]] && read -p "Please provide tenant name " PARAM_1
				curl -X GET  ${verbose_dict[$VERBOSE]}  \
				"http://${MANAGEMENT_API_IP}:${MANAGEMENT_API_PORT}/tenants/${PARAM_1}/endpoints" \
				-H "accept: application/json" \
				-H "Authorization: ${TOKEN}" -H "Content-Type: application/json"
				;;
			model | models | m)
				;;
		esac
		;;
	upload | u)
		[[ -z ${RESOURCE} ]] && read -p "Please provide model path " RESOURCE
		[[ -z ${PARAM_1} ]] && read -p "Please provide model name " PARAM_1
		[[ -z ${PARAM_2} ]] && PARAM_2=1
		[[ -z ${PARAM_3} ]] && read -p "Please provide tenant name " PARAM_3
		python model_upload_cli.py ${RESOURCE} ${PARAM_1} ${PARAM_2} ${PARAM_3}
		;;
	run-inference | ri)
		echo "Running inference"
		[[ -z ${RESOURCE} ]] && read -p "Please provide endpoint ip with port (grpc address) " RESOURCE
		[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
		[[ -z ${PARAM_2} ]] && read -p "Please provide model name " PARAM_2
		[[ -z ${PARAM_3} ]] && read -p "Please specify input type: list/numpy " PARAM_3
		[[ -z ${PARAM_4} ]] && read -p "Please provide images (type: ${PARAM_3}) " PARAM_4
		[[ -z ${PARAM_5} ]] && read -p "Please provide batch size " PARAM_5
		[[ -z ${PARAM_6} ]] && read -p "Please provide path to server cert " PARAM_6
		[[ -z ${PARAM_7} ]] && read -p "Please provide path to client cert " PARAM_7
		[[ -z ${PARAM_8} ]] && read -p "Please provide path to client key  " PARAM_8
		case "${PARAM_3}" in
				list)   INPUT_TYPE="--images_list"
					;;
				numpy)  INPUT_TYPE="--images_numpy_path"
					;;
				*)  echo "Wrong input type, choose list or numpy"
					exit 0
					;;
		esac
		python ../examples/grpc_client/grpc_client.py --grpc_address ${RESOURCE} --endpoint_name ${PARAM_1} \
		--model_name ${PARAM_2} ${INPUT_TYPE} ${PARAM_4} --batch_size ${PARAM_5} --server_cert ${PARAM_6} \
		--client_cert ${PARAM_7} --client_key ${PARAM_8}
		;;
	*)	show_help
		exit 0
		;;
esac
