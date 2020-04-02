import torch
import numpy as np
from tqdm.auto import tqdm
from torch.utils.data import DataLoader

from models import deeplabv3
from utils.dataset.GeoTiffDataset import GeoTiffDataset, GeoTiffWriter
from utils.dataset.transforms import transforms

model_checkpoint_path = "checkpoints/deeplabv3/deeplabv3_310320.pt"
num_classes = 2
batch_size = 16


def predict_tiff(model, img_path, dest_path, device, transform, crop_size=200, batch_size=8):
    """
    Predict segmentation classes on a geotiff image.
    Args:
        model: A PyTorch Model class
        img_path: Path to the image to classify
        dest_path: Location to save the new image
        device: A torch device
        crop_size: Size of patches to predict on before stitching them back together
        batch_size: The size of mini images to process at one time. Must be greater than 1.

    Returns: str Path to classified GeoTiff segmentation
    """
    model.eval()
    ds = GeoTiffDataset(img_path, transform, crop_size=crop_size)
    writer = GeoTiffWriter(ds, dest_path)

    dataloader = DataLoader(ds, batch_size, shuffle=False, num_workers=1, pin_memory=True)

    for i, xs in enumerate(tqdm(iter(dataloader))):
        xs = xs.to(device)

        # Do segmentation
        segmentation = model(xs)['out']

        # torch.cuda.synchronize() # For profiling only
        segmentation = segmentation.detach().cpu().numpy()
        segmentation = np.argmax(segmentation, axis=1)
        segmentation = np.expand_dims(segmentation, axis=1)
        segmentation = segmentation.astype(np.uint8)

        # Save part of tiff wither rasterio
        for j, seg in enumerate(segmentation):
            writer.write_index(i*batch_size + j, seg)


if __name__ == '__main__':
    if torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    model = deeplabv3.create_model(num_classes).to(device)
    checkpoint = torch.load(model_checkpoint_path)
    model.load_state_dict(checkpoint)

    transform = transforms.test_transforms

    predict_tiff(model,
                 "data/kelp/mcnaughton_2017/imagery/CentralCoast_McNaughtonGroup_MOS_U0168.tif",
                 "data/kelp/mcnaughton_2017/imagery/CentralCoast_McNaughtonGroup_MOS_U0168_kelp.tif",
                 device, transform, batch_size=batch_size)