show_help() {
cat << EOF
Usage: 
${0##*/} [-h?qskdz]
Required optons:
    -k - cluster name
    -d - domain name
Additional options
    -z - GCE cluster zone (if using kops and GCE)
    -q - silent mode (shows only important logs)
    -s - skip cluster creation via kops
    -h/? - show help
Usage examples  
    ${0##*/} -k <name> -d <domain>
    ${0##*/} -k <name> -d <domain> -z <gce_zone>
    ${0##*/} -k <name> -d <domain> -s -q
EOF
}
