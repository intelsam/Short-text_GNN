# coding=utf-8
# !/usr/bin/python3.6  # Please use python 3.6
"""
__synopsis__    : Reads CSV file as DF using pandas.
__description__ : Details and usage.
__project__     : Tweet_GNN_inductive
__classes__     :
__variables__   :
__methods__     :
__author__      : Samujjwal
__version__     : ":  "
__date__        : "07/05/20"
__last_modified__:
__copyright__   : "Copyright (c) 2020, All rights reserved."
__license__     : "This source code is licensed under the MIT-style license
                   found in the LICENSE file in the root directory of this
                   source tree."
"""

from os.path import join, exists
from pathlib import Path
from json import load, dumps
from collections import OrderedDict
from sklearn.preprocessing import MultiLabelBinarizer

from Logger.logger import logger
from Utils.utils import json_keys2df
from config import configuration as cfg, platform as plat, username as user


def read_json(file_path: str = join(cfg["paths"]["dataset_dir"][plat][
                                        user], 'acronym.json')) -> OrderedDict:
    """ Reads json file as OrderedDict.

    :param file_path:
    :return:
    """
    # file_path = Path(file_path + ".json")
    file_path = Path(file_path)
    logger.info(f"Reading json file [{file_path}].")

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            json_dict = OrderedDict(load(file))
        return json_dict
    else:
        raise FileNotFoundError("File [{}] not found.".format(file_path))


def save_json(data, filename, file_path='', overwrite=False, indent=2,
              date_time_tag=''):
    """

    :param data:
    :param filename:
    :param file_path:
    :param overwrite:
    :param indent:
    :param date_time_tag:
    :return:
    """
    logger.info(("Saving JSON file: ",
                 join(file_path, date_time_tag + filename + ".json")))
    if not overwrite and exists(
            join(file_path, date_time_tag + filename + ".json")):
        logger.error("File already exists and Overwrite == False.")
        return True
    try:
        with open(join(file_path, date_time_tag + filename + ".json"),
                  'w') as json_file:
            try:
                json_file.write(dumps(data, indent=indent))
            except Exception as e:
                logger.warning(("Could not write to json file:",
                                join(file_path, filename)))
                logger.warning(("Failure reason:", e))
                logger.warning(("Writing json as string:",
                                join(file_path, date_time_tag + filename + ".json")))
                json_file.write(dumps(str(data), indent=indent))
                return True
        json_file.close()
        return True
    except Exception as e:
        logger.warning(f"Could not write to json file: ["
                       f"{join(file_path, filename)}]")
        logger.warn(f"Failure reason: [{e}]")


mlb = MultiLabelBinarizer()


def read_labelled_json(data_dir=cfg["paths"]["dataset_dir"][plat][user],
                       filename=cfg["data"]["source"]['labelled'],
                       data_keys=['text', 'classes'], dataname='train',
                       # rename_cols={"parsed_tweet": "text"},
                       ):
    """ Reads json data and converts to DataFrame.

    Args:
        data_dir:
        filename:
        data_keys:
        dataname:
        rename_cols:

    Returns:

    """
    data_df = json_keys2df(data_keys, json_filename=filename,
                           dataset_dir=data_dir)
    logger.info(data_df.head())
    # data_df = data_df.rename(columns=rename_cols)

    if dataname == 'train':
        y_hot = mlb.fit_transform(data_df.classes.to_list())
    else:
        y_hot = mlb.transform(data_df.classes.to_list())

    for i in range(y_hot.shape[1]):
        data_df[i] = y_hot[:, i:i + 1]

    data_df = data_df.drop(columns=['classes'], axis=0)

    return data_df