import fire

from kelp.predictor import predict
from kelp.presence.trainer import train

if __name__ == '__main__':
    fire.Fire({
        'train': train,
        'pred': predict
    })
