from tqdm import tqdm
import os
import numpy as np
import random
import pandas as pd
import config as cfg
from metrics import target_distribution, nmi, ari, acc
from build_features import get_filenames_list, create_tensors
from predict import pred_dcec
from CAE import init_kmeans


def gamma_function(ite):
    return 1e-3 + (1-1/ite)*1e-3


def train_val_DCEC(
        maxiter, update_interval, save_interval, x_train, y_train, x_val,
        y_val, y_pred_last, model, tol, index, dcec_bs, dictionary,
        path_models_dcec, tables, exp
        ):

    # Init loss
    train_loss = [0, 0, 0]
    val_loss = [0, 0, 0]

    # Train and val
    for ite in tqdm(range(int(maxiter))):
        if ite % update_interval == 0:
            # if ite == 0:
            #     gamma = 1e-3
            # else:
            #     gamma = gamma_function(ite)
            #     print(gamma)
            model.compile(
                loss=['kld', 'mse'],
                loss_weights=[cfg.gamma, 1],
                optimizer=cfg.dcec_optim
            )
            q, _ = model.predict(x_train, verbose=0)
            p = target_distribution(q)
            val_q, _ = model.predict(x_val, verbose=0)
            val_p = target_distribution(val_q)

            # Evaluate the clustering performance
            y_train_pred = q.argmax(1)
            if y_train is not None:
                train_acc = np.round(acc(y_train, y_train_pred), 5)
                train_nmi = np.round(nmi(y_train, y_train_pred), 5)
                train_ari = np.round(ari(y_train, y_train_pred), 5)
                train_loss = np.round(train_loss, 5)
                print('\nIter {}: train acc={}, train nmi={}, train ari={}, train loss={}'.format(
                        ite, train_acc, train_nmi, train_ari, train_loss))

            y_val_pred = val_q.argmax(1)
            if y_val is not None:
                val_acc = np.round(acc(y_val, y_val_pred), 5)
                val_nmi = np.round(nmi(y_val, y_val_pred), 5)
                val_ari = np.round(ari(y_val, y_val_pred), 5)
                val_loss = np.round(val_loss, 5)
                print('Iter {}: val acc={}, val nmi={}, val ari={}, val loss={}'.format(
                    ite, val_acc, val_nmi, val_ari, val_loss))

            # Check stop criterion on train -> TODO on validation?
            diff = [f for f, i in enumerate(y_train_pred) if f != y_pred_last[i]]
            delta_label = np.sum(diff).astype(
                np.float32) / y_train_pred.shape[0]
            y_pred_last = np.copy(y_train_pred)
            if ite > 0 and delta_label < tol:
                print('delta_label ', delta_label, '< tol ', tol)
                print('Reached tolerance threshold. Stopping training.')
                break

        # Train on batch
        x_train_batch = np.array(random.sample(list(x_train), dcec_bs))
        train_p_batch = np.array(random.sample(list(p), dcec_bs))
        train_loss = model.train_on_batch(
            x=x_train_batch,
            y=[train_p_batch, x_train_batch]
        )

        # Validation on batch
        x_val_batch = np.array(random.sample(list(x_val), dcec_bs))
        val_p_batch = np.array(random.sample(list(val_p), dcec_bs))
        val_loss = model.test_on_batch(
            x=x_val_batch,
            y=[val_p_batch, x_val_batch]
        )

        # Save metrics to dict for csv
        dictionary['iteration'].append(ite)
        dictionary['train_loss'].append(train_loss[0])
        dictionary['val_loss'].append(val_loss[0])
        dictionary['clustering_loss'].append(train_loss[1])
        dictionary['val_clustering_loss'].append(val_loss[1])
        dictionary['reconstruction_loss'].append(train_loss[2])
        dictionary['val_reconstruction_loss'].append(val_loss[2])
        dictionary['train_acc'].append(train_acc)
        dictionary['val_acc'].append(val_acc)
        dictionary['train_nmi'].append(train_nmi)
        dictionary['val_nmi'].append(val_nmi)
        dictionary['train_ari'].append(train_ari)
        dictionary['val_ari'].append(val_ari)

        # Save model checkpoint
        if ite % save_interval == 0:
            os.makedirs(os.path.join(exp, path_models_dcec), exist_ok=True)
            model.save_weights(
                os.path.join(
                    exp, path_models_dcec, 'dcec_model_'+str(ite)+'.h5'))
        ite += 1

        # Save the trained model
        model.save_weights(
            os.path.join(path_models_dcec, 'dcec_model_final.h5'))

        # Save metrics to csv
        df = pd.DataFrame(data=dictionary)
        # df.to_csv(os.path.join(
        #     tables, exp, 'dcec_train_metrics.csv'), index=False)


def main():
    # Get datasets
    directories, file_list = get_filenames_list(cfg.processed_data)
    x_train, y_train, x_val, y_val, x_test, y_test = create_tensors(
        file_list, directories)

    model, y_pred_last = init_kmeans(
        cae=cfg.cae,
        n_clusters=cfg.n_clusters,
        ce_weights=cfg.ce_weights,
        n_init_kmeans=cfg.n_init_kmeans,
        x=x_test,
        y=y_test,
        gamma=cfg.gamma
    )

    train_val_DCEC(
        exp=cfg.exp,
        maxiter=cfg.maxiter,
        update_interval=cfg.update_interval,
        save_interval=cfg.save_interval,
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        y_val=y_val,
        y_pred_last=y_pred_last,
        model=model,
        tol=cfg.tol,
        index=cfg.index,
        dcec_bs=cfg.dcec_bs,
        dictionary=cfg.d,
        path_models_dcec=os.path.join(cfg.models, cfg.exp, 'dcec'),
        tables=cfg.tables
    )

    pred_dcec(
        model=model,
        weights=os.path.join(
            cfg.models, cfg.exp, 'dcec', 'dcec_model_final.h5'),
        directory=cfg.test_data,
        scans=cfg.scans,
        figures=cfg.figures,
        exp=cfg.exp,
        n=random.randint(0, 20)
    )

    print('done.')


if __name__ == "__main__":
    main()
