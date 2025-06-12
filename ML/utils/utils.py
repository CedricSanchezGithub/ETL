import matplotlib.pyplot as plt

from ML.ML_wildlens import train_loader, train_df, df_all


def afficher_echantillon(dataloader=train_loader, n=10):

    # Répartition des classes dans le train
    class_counts = train_df["nom_fr"].value_counts().sort_index()
    class_counts.plot(kind="bar", figsize=(10, 4))
    plt.title("Répartition des images par classe (nom_fr) - TRAIN")
    plt.xlabel("Animaux")
    plt.ylabel("Nombre d'images")
    plt.grid(True)
    plt.show()

    df_all["id_etat"].replace({1: "train", 2: "val", 3: "test"}).value_counts().plot(
        kind="bar", title="Répartition globale des images par split"
    )

    import seaborn as sns

    df_all["split"] = df_all["id_etat"].replace({1: "train", 2: "val", 3: "test"})

    plt.figure(figsize=(12, 6))
    sns.countplot(data=df_all, x="nom_fr", hue="split")
    plt.title("Répartition des images par classe et split")
    plt.xlabel("ID de l'espèce")
    plt.ylabel("Nombre d'images")
    plt.legend(title="Split")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def tracer_courbes_performance(train_losses, train_accuracies, val_accuracies):
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(train_losses, marker='o')
    plt.title("Train Loss par époque")
    plt.xlabel("Époque")
    plt.ylabel("Loss")

    plt.subplot(1, 2, 2)
    plt.plot(train_accuracies, label="Train Acc", marker='o')
    plt.plot(val_accuracies, label="Val Acc", marker='s')
    plt.title("Accuracy (Train vs Val)")
    plt.xlabel("Époque")
    plt.ylabel("Accuracy (%)")
    plt.legend()

    plt.tight_layout()
    plt.show()