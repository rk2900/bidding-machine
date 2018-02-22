import numpy as np

INTVL = False

#--- data folder ---#
data_folder = "../../make-ipinyou-data/"
train_postfix = "/train.yzx.txt"
test_postfix = "/test.yzx.txt"

output_folder = "../output/"

campaign_list = [1458, 2259, 2261, 2821, 2997, 3358, 3386, 3427, 3476]
campaign = 100000

#--- training hyper parameter ---#
model_list = ['rr', 'eu']
model_name = ''
laplace = 3
interval = 5
budget_prop = 1

lr_train_round = 20
lr_alpha = 5E-3
lr_lambda = 1E-4
eu_lambda = 1E-2

eu_train_round = 30
eu_scale = 10
ds_ratio = 0
mu_range = np.arange(-0.99, 0.99, 0.01)
#np.arange(-0.8, 0.1, 0.1).extend(np.arange(-0.1, 0.1, 0.01).extend(np.arange(0.1, 0.9, 0.1)))

em_scale = 1E-3
em_round = 30

#--- debug parameter ---#
math_err_num = 0


#--- replay parameter ---#
test_progress_unit = 0.1
train_progress_unit = 0.25
budget_props = [128, 64, 32, 16, 8, 4, 2, 1]

#--- draw parameter ---#
colors = {'lr':'cx--', 'rr':'or-', 'eu':'kp-', 'sqlr':'*b--'}

#--- market parameter ---#
DEBUG = False
PARAM_MARKET = False

campaign_id = 2997

market_train_round = 100
market_alpha = 1E-5
market_lambda = 5E-2

ds_flag = False
