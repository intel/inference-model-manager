import argparse
import glob
import numpy as np
from PIL import Image


def image_to_array(file_path):
    image = Image.open(file_path)
    if not image.size == (224, 224):
        image = image.resize((224, 224))
    image.load()
    data = np.asarray(image, dtype="float32")
    data = np.expand_dims(data, axis=0)
    return data


def load_images_from_list(images_list, image_size, number_of_images):
    print(f'Number of images: {number_of_images}')
    images = np.zeros((0, image_size, image_size, 3), np.dtype('<f'))
    for image in images_list:
        image_data = image_to_array(image)
        images = np.append(images, image_data, axis=0)
    return images


def load_images_from_dir(images_dir, image_size, number_of_images):
    if images_dir[-1] not in '/':
        images_dir += '/'
    images_dir += "*"
    images = glob.glob(images_dir)
    counted_images = number_of_images if len(images) > number_of_images else len(images)

    images = load_images_from_list(images, image_size, counted_images)
    return images


def save_images_to_numpy(output_name, images):
    np.save(output_name, images)


def main():
    parser = argparse.ArgumentParser(description='Convert images to numpy arrays')
    images = parser.add_mutually_exclusive_group(required=True)
    images.add_argument('--images_list', help='List of images in .jpg format')
    images.add_argument('--images_dir', help='Folder with images')
    parser.add_argument('--image_size', required=False, default=224,
                       help='Size of images. Default: 224')
    parser.add_argument('--number_of_images', required=False, default=1,
                        help='Number of images. Default: 1')
    parser.add_argument('--output', required=False, default='imgs.npy',
                        help='Output file name (numpy formatted). Default: ./imgs.npy')
    args = vars(parser.parse_args())

    number_of_images = int(args['number_of_images'])
    if args['images_list']:
        images_list = args['images_list'].split(',')
        images = load_images_from_list(images_list, args['image_size'], number_of_images)
    if args['images_dir']:
        images_dir = args['images_dir']
        images = load_images_from_dir(images_dir, args['image_size'], number_of_images)

    save_images_to_numpy(args['output'], images)

if __name__ == "__main__":
    main()
