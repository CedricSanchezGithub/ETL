import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

def afficher_echantillon(train_df, df_all):
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

def afficher_matrice_confusion(true_labels, predicted_labels, idx_to_label,
                                   titre="Matrice de confusion - Test final", cmap="Greens"):

        cm = confusion_matrix(true_labels, predicted_labels)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                      display_labels=[idx_to_label[i] for i in range(len(cm))])
        fig, ax = plt.subplots(figsize=(10, 10))
        disp.plot(xticks_rotation='vertical', ax=ax, cmap=cmap)
        plt.title(titre)
        plt.tight_layout()
        plt.show()


from sklearn.metrics import classification_report
import pandas as pd


def generer_rapport_classification(true_labels, predicted_labels, idx_to_label, arrondi=2, afficher=True):

    report = classification_report(
        true_labels,
        predicted_labels,
        target_names=[idx_to_label[i] for i in range(len(idx_to_label))],
        output_dict=True
    )
    df_report = pd.DataFrame(report).transpose()
    df_report_rounded = df_report.round(arrondi)

    if afficher:
        display(df_report_rounded.head(len(idx_to_label)))

    return df_report_rounded
