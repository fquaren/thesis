import os
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.cluster import KMeans


scans = ['CT', 'MRI', 'PET']
n_clusters = 3  # len(scans)

# Paths
processed_data = '/home/fquaren/unimib/tesi/data/processed/'
numpy = '/home/fquaren/unimib/tesi/data/processed/numpy'

CT = '/home/fquaren/unimib/tesi/data/raw/CT'
MRI = '/home/fquaren/unimib/tesi/data/raw/MRI'
PET = '/home/fquaren/unimib/tesi/data/raw/PET'
# train:    ct-2, ct-3,    mri-1, mri-3,    pet-2, pet-3
# val:      ct-4, ct-5,    mri-5, mri-6,    pet-4
# test:     ct-1,          mri-2,           pet-1
train_directory = '/home/fquaren/unimib/tesi/data/raw/train'
val_directory = '/home/fquaren/unimib/tesi/data/raw/val'
test_directory = '/home/fquaren/unimib/tesi/data/raw/test'
models = '/home/fquaren/unimib/tesi/models'
tables = '/home/fquaren/unimib/tesi/data/tables'
figures = '/home/fquaren/unimib/tesi/reports/figures'
experiments = '/home/fquaren/unimib/tesi/experiments'

exp = 'ASPC_FINAL'

ae_models = os.path.join(models, exp, 'ae')
ae_weights = os.path.join(models, exp, 'ae', 'ae_weights')
ce_weights = os.path.join(models, exp, 'ae', 'ce_weights')
final_encoder_weights = os.path.join(models, exp, 'final_encoder_weights')

# Pretrain ae settings
pretrain_epochs = 10000
ae_batch_size = 16
my_callbacks = [
    EarlyStopping(patience=25, monitor='val_loss'),
    ModelCheckpoint(
        filepath=ae_weights,
        save_best_only=True,
        save_weights_only=True,
        monitor='val_loss'
    )
]

kmeans = KMeans(
    n_clusters=n_clusters,
    n_init=100,
    random_state=0
)

# random state 0 ->
# random stato 1 -> TEST ACC = 0.0972972972972973; TEST NMI = 0.2990961625065741
# random state 2 -> VAL ACC = 0.3081081081081081; VAL NMI = 0.2990961625065741
# random state 3 -> 

# Pandas dataframe
dict_metrics = {
    'train_acc': [],
    'val_acc': [],
    'train_nmi': [],
    'val_nmi': [],
}

random_state_acc = {
    'random_state': [],
    'acc': [],
    'nmi': [],
}

final_random_state_acc = {
    'random_state': [],
    'test_acc': [],
    'test_nmi': [],
}
