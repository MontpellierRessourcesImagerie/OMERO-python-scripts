# TODO: Fix image namings
# TODO: FIx channel correspondance
# TODO: Remove iteration over two images and loading images from disk
# TODO: rename channels to object type

import numpy as np
import omero_toolbox as omero
from getpass import getpass

# Define variables
HOST = 'omero.mri.cnrs.fr'
PORT = 4064
CHANNELS_TO_SUM = (0, 1)


def sum_channels(image_array, channels):
    new_array = np.add(image_array[:, channels[0], ...], image_array[:, channels[1], ...])
    new_array = np.expand_dims(new_array, axis=1)
    return np.concatenate((image_array, new_array), axis=1)


if __name__ == '__main__':
    try:
        # Open the connection to OMERO
        conn = omero.open_connection(username=input("Username: "),
                                     password=getpass("OMERO Password: ", None),
                                     host=str(input('server (omero.mri.cnrs.fr): ') or HOST),
                                     port=int(input('port (4064): ') or PORT),
                                     group=input("Group: "))

        # get tagged images in dataset
        dataset_id = int(input('Dataset ID: '))
        dataset = omero.get_dataset(conn, dataset_id)
        project = dataset.getParent()

        new_dataset_name = f'{dataset.getName()}_summed'
        new_dataset_description = f'Source Dataset ID: {dataset.getId()}'
        new_dataset = omero.create_dataset(conn,
                                           name=new_dataset_name,
                                           description=new_dataset_description,
                                           parent_project=project)

        images = dataset.listChildren()

        for image in images:
            print(f'Analyzing image {image.getName()}')

            image_data = omero.get_intensities(image)
            new_image_data = sum_channels(image_data, CHANNELS_TO_SUM)
            channel_list = list(range(image.getSizeC()))
            channel_list.append(0)

            omero.create_image_from_numpy_array(connection=conn,
                                                data=new_image_data,
                                                image_name=f'{image.getName()}_SUM',
                                                image_description=f'Source Image ID:{image.getId()}',
                                                dataset=new_dataset,
                                                source_image_id=image.getId(),
                                                channels_list=channel_list,
                                                )

    finally:
        conn.close()
        print('Done')
