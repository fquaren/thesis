from features.build_features import get_filenames_list, create_tensors
import config as cfg


def pretrainCAE(x_train, x_val, batch_size, pretrain_epochs, my_callbacks):
    autoencoder, encoder = cfg.net
    encoder.summary()
    autoencoder.summary()
    autoencoder.compile(optimizer=cfg.optim, loss=cfg.cae_loss)
    autoencoder.fit(
        x_train,
        x_train,
        batch_size=batch_size,
        epochs=pretrain_epochs,
        validation_data=(x_val, x_val),
        callbacks=my_callbacks,
    )


if __name__ == "__main__":
    directories, file_list = get_filenames_list(cfg.processed_data)
    x_train, y_train, x_val, y_val, x_test, y_test = create_tensors(
        file_list, directories)
    pretrainCAE(
        x_train, x_val, cfg.batch_size, cfg.pretrain_epochs, cfg.my_callbacks)
    pass
