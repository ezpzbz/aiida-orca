curl -X POST https://content.dropboxapi.com/2/sharing/get_shared_link_file \
    --header "Authorization: Bearer $1" \
    --header "Dropbox-API-Arg: {\"url\": \"$2\",\"link_password\": \"$3\"}" \
    -o "./orca.tar.xz"
