import numpy as np
import omero_toolbox as omero
from omero import model
from getpass import getpass
import json

# Define variables
HOST = 'omero.mri.cnrs.fr'
PORT = 4064
ROI_COMMENTS = None
TEMP_DIR = '/run/media/julio/DATA/Amelie/'


try:
    # Open the connection to OMERO
    conn = omero.open_connection(username=input("Username: "),
                                 password=getpass("OMERO Password: ", None),
                                 host=str(input('server (omero.mri.cnrs.fr): ') or HOST),
                                 port=int(input('port (4064): ') or PORT),
                                 group=input("Group: "))

    dataset_id = int(input('Dataset ID: '))

    roi_filter = ROI_COMMENTS

    dataset = omero.get_dataset(conn, dataset_id)

    project = dataset.getParent()

    new_dataset_name = f'{dataset.getName()}_rois'
    new_dataset_description = f'Source Dataset ID: {dataset.getId()}'
    new_dataset = omero.create_dataset(conn,
                                       name=new_dataset_name,
                                       description=new_dataset_description,
                                       parent_project=project)

    images = dataset.listChildren()

    # Loop through images, get ROIs the intensity values, project and save as .npy
    roi_service = conn.getRoiService()

    for image in images:
        result = roi_service.findByImage(image.getId(), None)
        for roi in result.rois:
            shape = roi.getPrimaryShape()
            try:
                shape_comment = shape.getTextValue()._val
            except AttributeError:
                shape_comment = None
            if roi_filter is not None and shape_comment not in roi_filter:
                continue
            # data = omero.get_shape_intensities(image, shape)

            new_image_name = f'{image.getName().strip().split(".")[0]}_{shape_comment}'
            print(f'Processing image {new_image_name}')
            # np.save(f'{TEMP_DIR}{new_image_name}.npy', data)

            if isinstance(shape, model.PolygonI):
                shape_points = shape.getPoints()._val
                shape_points = [
                    tuple(float(c) for c in p.split(',')) for p in shape_points.split()
                ]
                image_x_coords = [int(x) for x, _ in shape_points]
                image_y_coords = [int(y) for _, y in shape_points]

                # Marking ROIs in GUI may render some coordinates out of bounds
                image_size_x = image.getSizeX()
                image_size_y = image.getSizeY()
                image_x_coords = [max(0, min(x, image_size_x)) for x in image_x_coords]
                image_y_coords = [max(0, min(y, image_size_y)) for y in image_y_coords]

                shape_x_pos = min(image_x_coords)
                shape_y_pos = min(image_y_coords)
                shape_points = [[x - shape_x_pos, y - shape_y_pos] for x, y in zip(image_x_coords, image_y_coords)]

                with open(f'{TEMP_DIR}{new_image_name}_points.txt', 'w') as text_file:
                    text_file.write(json.dumps(shape_points))

        print(f'Processed image {new_image_name}')

finally:
    conn.close()
    print('Done')
