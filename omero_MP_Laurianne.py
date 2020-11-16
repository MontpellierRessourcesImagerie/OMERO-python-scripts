import numpy as np
import omero_toolbox as omero
from getpass import getpass

# Define variables
HOST = 'omero.mri.cnrs.fr'
PORT = 4064
DIR = '/run/media/julio/DATA/Laurianne/AIP/'


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

        images = dataset.listChildren()

        for image in images:
            print(f'Analyzing image {image.getName()}')

            image_data = omero.get_intensities(image)
            np.save(f'{DIR}{image.getName()}_AIP', image_data)

    finally:
        conn.close()
        print('Done')
