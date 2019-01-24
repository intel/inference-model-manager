#
# Copyright (c) 2018-2019 Intel Corporation
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


import argparse
import glob
import numpy as np
import cv2


def crop_resize(img, crop_x, crop_y):
    y, x, c = img.shape
    y = crop_y if y < crop_y else y
    x = crop_x if x < crop_x else x
    img = cv2.resize(img, (x, y))
    start_x = x//2-(crop_x // 2)
    start_y = y//2-(crop_y // 2)
    return img[start_y:start_y + crop_y, start_x:start_x + crop_x, :]


def get_jpeg(path, size):
    with open(path, mode='rb') as file:
        content = file.read()

    img = np.frombuffer(content, dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)  # BGR format
    # retrieved array has BGR format and 0-255 normalization
    # add image preprocessing if needed by the model
    img = crop_resize(img, size, size)
    img = img.astype('float32')
    img = img.reshape(1, size, size, 3)
    print(path, img.shape, "; data range:", np.amin(img), ":", np.amax(img))
    return img


def image_to_array(file_path, image_size):
    print("Converting: {},  size: {} to numpy array".format(file_path, image_size))
    img = get_jpeg(file_path, image_size)
    return img


def load_images_from_list(images_list, image_size, number_of_images):
    print(f'Number of images: {number_of_images}')
    images = np.zeros((0, image_size, image_size, 3), np.dtype('<f'))
    for image in images_list:
        image_data = image_to_array(image, image_size)
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
