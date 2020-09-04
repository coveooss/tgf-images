set -e

# If GIT_TAG is not set, we recuperate the last tag for the repo
: ${GIT_TAG:=$(git describe --abbrev=0 --tags)}

# If the tag does not start with image- we ignore it
[ "${GIT_TAG::1}" != v ] && exit 0

for df in Dockerfile*
do
    echo
    printf '%40s\n' | tr ' ' -
    printf "Processing file $df\n"
    tag=${df:13}
    tag=${tag,,}
    [ -z ${tag} ] || tag=-${tag}
    git_tag=${GIT_TAG:1}
    git_maj_min=${git_tag%.*}
    version=ghcr.io/coveooss/tgf:${git_tag}${tag}
    version_mm=ghcr.io/coveooss/tgf:${git_maj_min}${tag}
    latest=${tag:1}
    latest=ghcr.io/coveooss/tgf:${latest:-latest}

    # We do not want to tag latest if this is not an official version number
    [[ $git_tag == *-* ]] && unset latest
    
    dockerfile=dockerfile.temp
    # We replace the GIT_TAG variable if any (case where the image is build from another image)
    # The result file is simply named Dockerfile
    cat $df | sed -e "s/\${GIT_TAG}/$git_tag/" | sed -e "s/\TGF_IMAGE_MAJ_MIN=/TGF_IMAGE_MAJ_MIN=$git_maj_min/" > $dockerfile

    docker build -f $dockerfile -t $version . && rm $dockerfile
    docker push $version
    if [ -n "$latest" ]
    then 
        # docker tag $version $latest && docker push $latest (we do not update latest on old version)
        docker tag $version $version_mm && docker push $version_mm
    fi
done
