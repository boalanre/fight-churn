import pandas as pd
import numpy as np
import os

from listing_7_5_fat_tail_scores import transform_fattail_columns, transform_skew_columns

def reload_churn_data(data_set_path,suffix,listing,is_customer_data):
    data_path = data_set_path.replace('.csv', '_{}.csv'.format(suffix))
    assert os.path.isfile(data_path),'You must run listing {} to save {} first'.format(listing,suffix)
    ic = [0,1] if is_customer_data else 0
    churn_data = pd.read_csv(data_path, index_col=ic)
    return churn_data

def rescore_metrics(data_set_path='', save=True):

    load_mat_df = reload_churn_data(data_set_path,'load_mat','6.4',is_customer_data=False)
    score_df = reload_churn_data(data_set_path,'score_params','7.5',is_customer_data=False)
    current_data = reload_churn_data(data_set_path,'current','8.2',is_customer_data=True)
    assert set(score_df.index.values)==set(current_data.columns.values),"Data to re-score does not match transform params"
    assert set(load_mat_df.index.values)==set(current_data.columns.values),"Data to re-score does not match load matrix"

    transform_skew_columns(current_data,score_df[score_df['skew_score']].index.values)

    transform_fattail_columns(current_data,score_df[score_df['skew_score']].index.values)

    current_data=current_data[score_df.index.values]

    scaled_data=(current_data-score_df['mean'])/score_df['std']

    scaled_data = scaled_data[load_mat_df.index.values]
    grouped_ndarray = np.matmul(scaled_data.to_numpy(), load_mat_df.to_numpy())

    grouped_column_names = ['metric_group_%d' % (d + 1) for d in range(0, load_mat_df.shape[1])]
    current_data_grouped = pd.DataFrame(grouped_ndarray,columns=grouped_column_names, index=current_data.index)

    if save:
        score_save_path=data_set_path.replace('.csv','_current_groupscore.csv')
        current_data_grouped.to_csv(score_save_path,header=True)
        print('Saving results to %s' % score_save_path)

    return current_data_grouped