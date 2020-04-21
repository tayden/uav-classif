# Get the path to this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Make output dirs
mkdir -p "./train_output/checkpoints"
mkdir -p "./train_output/model"
mkdir -p "./train_output/segmentation"

# Example build and run command
docker build --file ../Dockerfile --compress --tag deeplabv3/kelp ../..

docker run -it --rm \
-v "$DIR/train_input":/opt/ml/input \
-v "$DIR/train_output":/opt/ml/output \
--user "$(id -u):$(id -g)" \
--ipc host \
--gpus all \
--name kelp-pred \
deeplabv3/kelp pred