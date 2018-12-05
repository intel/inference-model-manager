#!/bin/bash
#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

show_help() {
cat << EOF
Usage: 
	${0##*/} [-vhapc] [OPERATION] [RESOURCE] [_ADDITIONAL_PARAMS_]
Options:
	v - verbose mode, prints simplified cURL (vv - prints full cURL)
	h - help
	a - management api address (could be provided with MANAGEMENT_API_ADDRESS env or from config file)
	p - management api port (could be provided with MANAGEMENT_API_PORT env or from config file)
	c - path to config file
Examples: 
	.${0##*/} -a mgmt.example.com -p 443 -v create tenant mytenant
	.${0##*/} create t mytenant myscope
	.${0##*/} create e myendpoint mymodel
	.${0##*/} -a 127.0.0.1 login
	.${0##*/} logout
	.${0##*/} run-inference 127.0.0.1 443 numpy imgs.npy 10 mymodel server.crt client.crt client.key
Operations:
	create (c), remove (rm), update (up), scale (s), list (ls), login, logout, upload (u), run-inference (ri)
Resources:
	tenant (t), endpoint (e), model (m)
Environment variables:
	IMM_CONFIG_PATH - Inference Model Manager config file
	MANAGEMENT_API_ADDRESS - management api address
	MANAGEMENT_API_PORT - management api port
	CERT - path to certificate for tenant creation
	MANAGEMENT_CA_CERT_PATH = path to ca-man-api.crt used for login
	TENANT_RESOURCES - quota used for tenant creation
	ENDPOINT_RESOURCES - quota used for endpoint creation
EOF
}

VERBOSE=0
OPTIND=1
DEFAULT_CFG_FILE=~/.imm
IMM_CONFIG_PATH=${IMM_CONFIG_PATH:=${DEFAULT_CFG_FILE}}

while getopts "hva:p:c:" opt; do
	case $opt in
		h)	show_help
			exit 0
			;;
		v)	let "VERBOSE++"
			;;
		a)	MANAGEMENT_API_ADDRESS=$OPTARG
			echo "Management api address: ${MANAGEMENT_API_ADDRESS}"
			;;
		p)	MANAGEMENT_API_PORT=$OPTARG
			echo "Management api port: ${MANAGEMENT_API_PORT}"
			;;
		c)	IMM_CONFIG_PATH=$OPTARG
			echo "Config file: ${IMM_CONFIG_PATH}"
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
PARAM_6=$8
PARAM_7=$9
PARAM_8=${10}

if [[ -s ${IMM_CONFIG_PATH} ]]; then
	TOKEN=`cat ${IMM_CONFIG_PATH} | jq -r '.id_token'`
	[[ -z "${MANAGEMENT_API_ADDRESS}" ]] && MANAGEMENT_API_ADDRESS=`cat ${IMM_CONFIG_PATH} | jq -r '.management_api_address'`
	[[ -z "${MANAGEMENT_API_PORT}" ]] && MANAGEMENT_API_PORT=`cat ${IMM_CONFIG_PATH} | jq -r '.management_api_port'`
elif [[ ${OPERATION} != "login" ]]; then
	echo "Please login first"
	exit 0
fi

MANAGEMENT_API_ADDRESS=${MANAGEMENT_API_ADDRESS:-'127.0.0.1'}
MANAGEMENT_API_PORT=${MANAGEMENT_API_PORT:-443}

CERT=${CERT}
TENANT_RESOURCES=${TENANT_RESOURCES:="{\"requests.cpu\": \"2\", \"requests.memory\": \"2Gi\", \"limits.cpu\": \"2\", \"limits.memory\": \"2Gi\", \"maxEndpoints\": 15}"}
ENDPOINT_RESOURCES=${ENDPOINT_RESOURCES:="{\"requests.cpu\": \"1\", \"requests.memory\": \"1Gi\", \"limits.cpu\": \"1\", \"limits.memory\": \"1Gi\"}"}

case "$OPERATION" in
	create | c) 
		case "$RESOURCE" in
			tenant | t) echo "Create tenant"
				[[ -z ${PARAM_1} ]] && read -p "Please provide tenant name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide scope (group name) " PARAM_2
				CURL='curl -s -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" \
					-d "{\"name\": \"${PARAM_1}\", \"cert\": \"${CERT}\", \"scope\":\"${PARAM_2}\",\"quota\": ${TENANT_RESOURCES}}" \
					-X POST "https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
			endpoint | e) echo "Create endpoint"
				[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide model name " PARAM_2
				[[ -z ${PARAM_3} ]] && read -p "Please provide model version " PARAM_3
				[[ -z ${PARAM_4} ]] && read -p "Please provide tenant name " PARAM_4
				CURL='curl -s -X POST \
				"https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants/${PARAM_4}/endpoints" \
				-H "accept: application/json" \
				-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" \
				-d "{\"modelName\":\"${PARAM_2}\", \"modelVersion\":${PARAM_3}, \"endpointName\":\"${PARAM_1}\", \"subjectName\": \"client\", \"resources\": ${ENDPOINT_RESOURCES}}"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
		esac
		;;
	remove | rm)
		case "$RESOURCE" in
			tenant | t)
				[[ -z ${PARAM_1} ]] && read -p "Please provide tenant name " PARAM_1
				CURL='curl -s -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json"  \
					-d "{\"name\": \"${PARAM_1}\"}" -X DELETE \
					"https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
			endpoint | e)
				[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide tenant name " PARAM_2
				CURL='curl -s -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json"  \
					-d "{\"endpointName\": \"${PARAM_1}\"}" -X DELETE \
					"https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants/${PARAM_2}/endpoints"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
			model | m)
				[[ -z ${PARAM_1} ]] && read -p "Please provide model name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide model version " PARAM_2
				[[ -z ${PARAM_3} ]] && read -p "Please provide tenant name " PARAM_3
				CURL='curl -X DELETE -s \
					"https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants/${PARAM_3}/models" -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" \
					-d "{\"modelName\": \"${PARAM_1}\", \"modelVersion\": ${PARAM_2}}"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
		esac
		;;
	update | up)
		case "$RESOURCE" in
			endpoint | e)
				[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide new model name " PARAM_2
				[[ -z ${PARAM_3} ]] && read -p "Please provide model version " PARAM_3
				[[ -z ${PARAM_4} ]] && read -p "Please provide tenant name " PARAM_4
				CURL='curl -X PATCH -s  \
				"https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants/${PARAM_4}/endpoints/${PARAM_1}" -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" \
					-d "{\"modelName\": ${PARAM_2}, \"modelVersion\":${PARAM_3}}"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
		esac
		;;
	scale | s)
		case "$RESOURCE" in
			endpoint | e)
				[[ -z ${PARAM_1} ]] && read -p "Please provide endpoint name " PARAM_1
				[[ -z ${PARAM_2} ]] && read -p "Please provide number of replicas " PARAM_2
				[[ -z ${PARAM_3} ]] && read -p "Please provide tenant name " PARAM_3
				CURL='curl -X PATCH -s  \
				"https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants/${PARAM_3}/endpoints/${PARAM_1}/replicas" -H "accept: application/json" \
					-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" \
					-d "{\"replicas\": ${PARAM_2}}"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
		esac
		;;
	login)
		echo "Signing in..."
		if [ -z "${MANAGEMENT_API_ADDRESS}" ]; then
			echo "Please provide management api address"
			read MANAGEMENT_API_ADDRESS
		fi
		[[ -z ${MANAGEMENT_CA_CERT_PATH} ]] && MANAGEMENT_CA_CERT_PATH="" || MANAGEMENT_CA_CERT_PATH="--ca_cert ${MANAGEMENT_CA_CERT_PATH}"
		python webbrowser_authenticate.py --address ${MANAGEMENT_API_ADDRESS} --port ${MANAGEMENT_API_PORT} ${MANAGEMENT_CA_CERT_PATH}
		TOKEN=`cat "${IMM_CONFIG_PATH}" | jq -r '.id_token'`
		echo ${TOKEN}
		;;
	logout)
		read -r -p "Are you sure? This will remove all tokens from your config file. [y/n] " response
		if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
			if [ -f ${IMM_CONFIG_PATH} ]; then
				CFG_WITHOUT_TOKENS=`cat ${IMM_CONFIG_PATH} | jq -c '{management_api_address, management_api_port}'`
				echo ${CFG_WITHOUT_TOKENS} > ${IMM_CONFIG_PATH}
				echo "Signed out"
			else
				echo "Config file ${IMM_CONFIG_PATH} does not exist"
			fi
		fi
		;;
	list | ls)	
		case "$RESOURCE" in
			tenant | tenants | t)
				CURL='curl -X GET -s -H "accept: application/json" \
				-H "Authorization: ${TOKEN}" -H "Content-Type: application/json" \
				https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
			endpoint | endpoints | e)
				[[ -z ${PARAM_1} ]] && read -p "Please provide tenant name " PARAM_1
				CURL='curl -X GET -s \
				"https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants/${PARAM_1}/endpoints" \
				-H "accept: application/json" -H "Authorization: ${TOKEN}" -H "Content-Type: application/json"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"
				;;
			model | models | m)
				[[ -z ${PARAM_1} ]] && read -p "Please provide tenant name " PARAM_1
				CURL='curl -X GET -s \
				"https://${MANAGEMENT_API_ADDRESS}:${MANAGEMENT_API_PORT}/tenants/${PARAM_1}/models" \
				-H "accept: application/json" -H "Authorization: ${TOKEN}" -H "Content-Type: application/json"'
				[[ ${VERBOSE} == 1 ]] && echo $CURL
				[[ ${VERBOSE} == 2 ]] && eval echo $CURL
				eval "$CURL"

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
		[[ -z ${RESOURCE} ]] && read -p "Please provide endpoint address with port (grpc address) " RESOURCE
		[[ -z ${PARAM_1} ]] && read -p "Please provide model name " PARAM_1
		[[ -z ${PARAM_2} ]] && read -p "Please specify input type: list/numpy " PARAM_2
		[[ -z ${PARAM_3} ]] && read -p "Please provide images (type: ${PARAM_2}) " PARAM_3
		[[ -z ${PARAM_4} ]] && read -p "Please provide batch size " PARAM_4
		[[ -z ${PARAM_5} ]] && read -p "Please provide path to server cert " PARAM_5
		[[ -z ${PARAM_6} ]] && read -p "Please provide path to client cert " PARAM_6
		[[ -z ${PARAM_7} ]] && read -p "Please provide path to client key  " PARAM_7
		case "${PARAM_2}" in
				list)   INPUT_TYPE="--images_list"
					;;
				numpy)  INPUT_TYPE="--images_numpy_path"
					;;
				*)  echo "Wrong input type, choose list or numpy"
					exit 0
					;;
		esac
		python ../examples/grpc_client/grpc_client.py ${RESOURCE} ${PARAM_1} \
		${INPUT_TYPE} ${PARAM_3} --batch_size ${PARAM_4} --server_cert ${PARAM_5} \
		--client_cert ${PARAM_6} --client_key ${PARAM_7} 
		;;
	*)	show_help
		exit 0
		;;
esac
