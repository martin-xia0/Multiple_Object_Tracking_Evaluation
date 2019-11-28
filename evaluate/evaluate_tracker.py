import os
import numpy as np
from numpy.core.multiarray import ndarray
from scipy import optimize
import pymysql


def load_annotation(filename):
    """load data from input txt

    params
    filename: file name of loading txt
    ---------
    return
    video: nXm matrix, contain n frames, each frame contains m objects
    frame_num: frame number of input txt
    obj_num: object num of each frame in time series
    ---------
    """
    txt = open(filename)
    result = txt.readlines()
    video = []
    frame = []
    obj_num = []
    frame_id = 0
    for line in result:
        person = line.split(',')
        if not len(person) == 0:
            if int(person[0]) == frame_id:
                frame.append(person)
            else:
                frame_id += 1
                obj_num.append(len(frame))
                video.append(frame)
                frame = [person]
    frame_num = frame_id
    print(video)
    print("Total frame of {} is {}".format(filename, frame_num))
    return video, frame_num, obj_num


def distance_matrix_series(gt_video, hp_video, frame_num):
    """

    params
    gt_video: ground truth frame series
    hp_video: hypothesis frame series
    frame_num: frame number of the video
    ----------
    return
    distance_matrix_series: distance_matrix of each frame in time series
    """
    distance_matrix_series = []
    for frame_id in range(frame_num):
        matrix = distance_matrix(gt_video[frame_id], hp_video[frame_id])
        distance_matrix_series.append(matrix)
        if frame_id == 0:
            print(matrix)
    return distance_matrix_series


def distance_matrix(gt_frame, hp_frame):
    """

    params
    gt_frame: ground truth frame
    hp_frame: hypothesis frame
    --------------
    return
    distance_matrix: distance between one pair (oi, hj) (euclid distance), each row represent one ground truth obj
    """
    distance_matrix = []
    for gt_obj in gt_frame:
        distance_row = []
        for hp_obj in hp_frame:
            distance = iou_distance(gt_obj, hp_obj)
            distance_row.append(distance)
        distance_matrix.append(distance_row)
    print(distance_matrix)
    return distance_matrix


def rectangle_distance(gt_obj, hp_obj):
    """

    params
    gt_obj: object in ground truth
    hp_obj: object in hypothesis
    ----------
    return
    distance: distance between two rectangles' centers
    """
    gt_central = np.array([int(gt_obj[2]) + int(gt_obj[3]) / 2, int(gt_obj[4]) + int(gt_obj[5]) / 2])
    hp_central = np.array([int(hp_obj[2]) + int(hp_obj[3]) / 2, int(hp_obj[4]) + int(hp_obj[5]) / 2])
    ham_dist = gt_central - hp_central  # type: ndarray
    distance = np.sqrt((ham_dist).dot(ham_dist))
    return distance


def iou_distance(gt_obj, hp_obj):
    """ calculate the iou coefficient 'intersection over union (IoU)' of one obj
    The IoU is computed as
        IoU(a,b) = 1. - isect(a, b) / union(a, b)
    where isect(a,b) is the area of intersection of two rectangles and union(a, b) the area of union. The
    IoU is bounded between zero and one. 0 when the rectangles overlap perfectly and 1 when the overlap is
    zero.
    we normally think if iou < 0.5, the matching is qualified

    param
    gt_obj:
    hp_obj:
    """
    gt_left_x = int(gt_obj[2])
    hp_left_x = int(hp_obj[2])
    gt_width = int(gt_obj[3])
    hp_width = int(hp_obj[3])
    gt_up_y = int(gt_obj[4])
    hp_up_y = int(hp_obj[4])
    gt_height = int(gt_obj[5])
    hp_height = int(hp_obj[5])

    # width
    x1 = gt_left_x - hp_left_x
    x2 = (gt_left_x + gt_width) - (hp_left_x + hp_width)
    y1 = gt_up_y - hp_up_y
    y2 = (gt_up_y + gt_height) - (hp_up_y + hp_height)
    if x1 * x2 > 0:
        width = max(0, ((gt_width + hp_width) - abs(x1 + x2))) / 2
    else:
        width = min(gt_width, hp_width)
    if y1 * y2 > 0:
        height = max(0, ((gt_height + hp_height) - abs(y1 + y2))) / 2
    else:
        height = min(gt_height, hp_height)

    iou_area = height * width
    total_area = hp_width * hp_width + gt_width * gt_height
    # print(width, height)
    # print("iou_area:{}").format(iou_area)
    # print("total_area:{}").format(total_area)
    iou = 1 - iou_area / total_area
    return iou


def mapping_series(distance_matrix_series):
    """ the hp_gt mapping in time series

    params
    distance_matrix_series
    --------------
    return
    mapping_series: matching pairs for each frame in time series
    distance_series: minimum distance series for each frame in time series
    """
    mapping_series = []
    distance_series = []
    test = 1
    for frame in distance_matrix_series:
        mapping, distance = mapping_frame(frame)
        mapping_series.append(mapping)
        distance_series.append(distance)
        if test:
            print(mapping)
            test = 0
    return mapping_series, distance_series


def mapping_frame(distance_matrix):
    mapping_frame = {}
    """using hungary algorithm to get the mapping pairs (oi, hj)
    thus minimize the total gt-hp distance error, we need the minimize the iou_distance
    
    params
    distance_matrix: distance matrix of one frame
    threshold: max distance to form a gt-hp pair
    -----------
    return
    mapping_frame: the mapping pairs for one frame{'oi': 'hj', 'oh': 'hl' ...}
    distance_frame: the minimum sum of distance for one frame
    """
    threshold = 0.5
    distance_frame = 0
    cost_matrix = np.array(distance_matrix)
    print("The shape of the distance array is {}".format(cost_matrix.shape))
    opt_gt_id, opt_hp_id = optimize.linear_sum_assignment(cost_matrix)

    assert len(opt_gt_id) == len(opt_hp_id)
    pre_pair_num = len(opt_gt_id)
    for i in range(pre_pair_num):
        gt_id = opt_gt_id[i]
        hp_id = opt_hp_id[i]
        distance_frame = distance_matrix[gt_id][hp_id]
        if distance_frame < threshold:
            mapping_frame[gt_id] = hp_id
    return mapping_frame, distance_frame


def MOTA_series(mapping_series, frame_num, gt_num, hp_num):
    """calculate the MOTA series of a video

    params
    mapping_series: mapping for the whole series
    frame_num: total number of frames
    gt_num: object num series of ground truth
    hp_num: object num series of hypothesis
    -----------
    return
    MOTA: MOTA for the whole series
    """
    MOTA_series = []
    for frame_id in range(frame_num):
        MOTA_series.append(MOTA_frame(mapping_series, frame_id, gt_num[frame_id], hp_num[frame_id]))
    return MOTA_series


def MOTA_frame(mapping_series, frame_id, gt_num, hp_num):
    """calculate MOTA of a frame

    params
    mapping_series: mapping for frame series
    frame_id: id of frame which is processing
    gt_num: object num of ground truth
    hp_num: object num of hypothesis
    -----------
    return
    MOTA: MOTA for a frame
    """
    if frame_id == 0:
        MOTA = 1
    else:
        mapping_prev = mapping_series[frame_id - 1]
        mapping_now = mapping_series[frame_id]
        mismatch = 0
        for gt_obj_pre in mapping_prev:
            hp_obj_pre = mapping_prev[gt_obj_pre]
            if gt_obj_pre in mapping_now.keys():
                hp_obj_now = mapping_now[gt_obj_pre]
                if hp_obj_pre != hp_obj_now:
                    mismatch += 1
        false_pos = hp_num - len(mapping_now)
        miss = gt_num - len(mapping_now)
        print('Frame {}, mismatch:{}, false_pos:{}, miss:{}'.format(frame_id, mismatch, false_pos, miss))
        MOTA = 1 - (mismatch + false_pos + miss) / gt_num
    return MOTA


def MOTP_series(mapping_series, distance_series, frame_num, gt_num, hp_num):
    """calculate the MOTP series of a video

    params
    mapping_series
    distance_series
    frame_num
    gt_num
    hp_num
    ----------------
    return
    MOTP_series
    """
    MOTP_series = []
    for frame_id in range(frame_num):
        MOTP = MOTP_frame(len(mapping_series[frame_id]), distance_series[frame_id], frame_id, gt_num[frame_id],
                          hp_num[frame_id])
        MOTP_series.append(MOTP)
    return MOTP_series


def MOTP_frame(pairs_num, distance, frame_id, gt_num, hp_num):
    """calculate MOTP of a frame

    params
    pairs_num: mapping pairs num for one frame
    distance:
    frame_id: id of frame which is processing
    gt_num: object num of ground truth
    hp_num: object num of hypothesis
    -----------
    return
    MOTP_frame: MOTP for a frame
    """
    MOTP_frame = distance / pairs_num
    return MOTP_frame


def evaluate_tracker(cursor, challenge_id, tracker_id, metrics_list, result_list):
    """fill in the evaluation result of a tracker.
    This tracker has already added in db when user create

    challenge_id
    tracker_id
    metrics_list: the metrics used to evaluate a tracker
    result_list: the evaluation result of the tracker

    return
    """
    result_sql = ""
    for i in range(len(metrics_list)):
        metrics = metrics_list[i]
        result = result_list[i]
        if i == len(metrics_list) - 1:
            result_sql += "{}={} ".format(metrics, result)
        else:
            result_sql += "{}={}, ".format(metrics, result)
    add_sql = "UPDATE TRACKER{} SET {} WHERE id={};".format(challenge_id, result_sql, tracker_id)
    print(add_sql)
    cursor.excute(add_sql)


if __name__ == '__main__':
    # conn = pymysql.Connect(
    #     host='localhost',
    #     port=3306,
    #     user='admin',
    #     passwd='abc.123',
    #     db='niewu',
    #     charset='utf8'
    # )
    # the tracker has already created, we now need to use the upload hypothesis files to get the evaluation results
    gt_video, gt_framenum, gt_objnum = load_annotation('mot_gt.txt')
    hp_video, hp_framenum, hp_objnum = load_annotation('mot_hp.txt')

    assert gt_framenum == hp_framenum
    frame_num = hp_framenum
    distance_matrix_series = distance_matrix_series(gt_video, hp_video, frame_num)
    mapping_series, distance_series = mapping_series(distance_matrix_series)
    MOTA_series = MOTA_series(mapping_series, frame_num, gt_objnum, hp_objnum)
    MOTP_series = MOTP_series(mapping_series, distance_series, frame_num, gt_objnum, hp_objnum)
    print(MOTA_series)
    print(MOTP_series)
    MOTA = sum(MOTA_series) / len(MOTA_series)
    MOTP = sum(MOTP_series) / len(MOTP_series)
    print("MOTA of this video is {}".format(MOTA))
    print("MOTP of this video is {}".format(MOTP))

