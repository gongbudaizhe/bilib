from __future__ import print_function

from time import time
import logging
import matplotlib.pyplot as plt

from sklearn.cross_validation import train_test_split
from sklearn.datasets import fetch_lfw_people
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.decomposition import RandomizedPCA
from sklearn.svm import SVC

from numpy import mean, ones, dot, real, unique, zeros, sum, eye, trace, diag
from numpy.linalg import eig, inv
from numpy.random import rand


class LegacyPCA:
    """Legacy PCA

    Get the eigenvectors and eigenvalues using ordinary eigenvector decomposition
    without any fancy tricks. It can be really slow with O(D**3) complexity where
    D is the feature dimension of training examples.

    Parameters
    ----------
    n_components : integer
        Number of components to keep.

    whiten : bool, optional
        When True (False by default) the components_ vectors are divided by n_samples
        times singular values to ensure uncorrelated outputs with unit component-wise
        variances.Whitening will remove some information from the transformed signal
        (the relative variance scales of the components) but can sometime improve the
         predictive accuracy of the downstream estimators by making there data respect
          some hard-wired assumptions

    """
    def __init__(self, n_components, whiten=True):
        self.n_components = n_components
        self.whiten = whiten

        self.mean_ = None

    def normalize_(self, X):
        """Normalize the data by substracting the mean. Optionally divide the standard deviation
        if whiten is true

        Parameters
        ----------
        X: array-like, shape (n_samples, n_features)
            Training data, where n_samples in the number of samples
            and n_features is the number of features.

        Returns
        -------
        X_normalized : array-like, shape(n_samples, n_features)
            Returns normalized X.
        """
        n_train_samples, n_features = X.shape
        mean_ = self.mean_

        X_normalized = X - dot(ones((n_train_samples, 1)), mean_.T)
        # if self.whiten:
        #     variance = (mean(X_normalized**2, axis=0)**0.5).reshape((n_features, 1))
        #     X_normalized = X_normalized / dot(ones((n_train_samples, 1)), variance.T)
        return X_normalized

    def fit(self, X):
        """Fit the model with X by extracting the first principal components.

        Parameters
        ----------
        X: array-like, shape (n_samples, n_features)
            Training data, where n_samples in the number of samples
            and n_features is the number of features.

        Returns
        -------
        self : object
            Returns the instance itself.
        """
        n_train_samples, n_features = X.shape
        self.mean_ = mean(X, axis=0).reshape((n_features, 1))

        X_normalized = self.normalize_(X)
        S = dot(X_normalized.T, X_normalized) / n_train_samples
        eigenvalues, eigenvectors = eig(S)
        index = eigenvalues.argsort()[::-1][:self.n_components]
        eigenvalues_of_components = real(eigenvalues[index])
        self.eigenvalues = eigenvalues_of_components
        self._L = diag(self.eigenvalues ** (-0.5))
        self.components_ = real(eigenvectors[:, index]).T
        return self

    def transform(self, X):
        """Apply dimensionality reduction on X.

        X is projected on the first principal components previous extracted
        from a training set.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            New data, where n_samples in the number of samples
            and n_features is the number of features.

        Returns
        -------
        X_new : array-like, shape (n_samples, n_components)

        """
        X_normalized = self.normalize_(X)
        X_transformed = dot(X_normalized, self.components_.T)
        if self.whiten:
            X_transformed = dot(X_transformed, self._L)
        return X_transformed


class EMPCA(LegacyPCA):
    """
        REFERENCE: Bishop
    """
    def __init__(self, n_components, whiten=True):
        self.n_components = n_components
        self.whiten = whiten

    def fit(self, X):
        n_iterations = 50
        n_samples, n_features = X.shape
        n_components = self.n_components
        W = rand(n_features, n_components)
        self.mean_ = mean(X, axis=0).reshape((n_features, 1))
        X_normalized = self.normalize_(X)

        # EM loop
        for i in range(n_iterations):
            Z = dot(inv(dot(W.T, W)), dot(W.T, X_normalized.T))
            W = dot(dot(X_normalized.T, Z.T), inv(dot(Z, Z.T)))

        X_transformed = dot(X_normalized, W)
        # approximate eigenvalues using X_train
        eigenvalues = mean(X_transformed**2, axis=0)
        self.components_ = W.T
        self.eigenvalues = eigenvalues
        self._L = diag(self.eigenvalues ** (-0.5))

        return self

    def fit_beta(self, X):
        n_iterations = 2
        n_samples, n_features = X.shape
        n_components = self.n_components

        # random initialization of parameters except mean
        self.mean_ = mean(X, axis=0).reshape((n_features, 1))
        X_normalized = self.normalize_(X)

        W = rand(n_features, n_components)
        variance = rand()

        # EM loop
        for i in range(n_iterations):
            print("iteration: %i" % i)
            t0 = time()
            inv_M = inv(dot(W.T, W) + variance * eye(n_components))
            print("duration:%0.3f" % (time() - t0))
            # accumulator of W, it has two matrices to accumulate
            W_acc = [zeros((n_features, n_components)), zeros((n_components, n_components))]
            variance_acc = [0, 0, 0]   # accumulator of variance
            E_z_list = []
            E_zzt_list = []
            for j in range(n_samples):
                print("samples: %i" % j)
                t0 = time()
                t1 = time()
                x = X_normalized[i, :].reshape((n_features, 1))    # Xn
                print("duration:%0.5f" % (time() - t0))
                t0 = time()
                E_z = dot(dot(inv_M, W.T), x)   # E[Zn]
                print("duration:%0.5f" % (time() - t0))
                t0 = time()
                E_zzt = variance * inv_M + dot(E_z, E_z.T)    # E[Zn Zn.T]
                print("duration:%0.5f" % (time() - t0))
                t0 = time()
                W_acc[0] += dot(x, E_z.T)
                W_acc[1] += E_zzt
                print("duration:%0.5f" % (time() - t0))
                t0 = time()
                E_z_list.append(E_z)
                E_zzt_list.append(E_zzt)
                print("duration:%0.5f" % (time() - t0))
                print("duration:%0.5f" % (time() - t1))

            W = dot(W_acc[0], inv(W_acc[1]))

            for j in range(n_samples):
                x = X_normalized[i, :].reshape((n_features, 1))    # Xn
                E_z = E_z_list[j]   # E[Zn]
                E_zzt = E_zzt_list[j]    # E[Zn Zn.T]

                variance_acc[0] += dot(x.T, x)
                variance_acc[1] += -2 * dot(dot(E_z.T, W.T), x)
                variance_acc[2] += trace(dot(E_zzt, dot(W.T, W)))
            variance = (variance_acc[0] + variance_acc[1] + variance_acc[2]) / (n_samples * n_features)
        self.variance = variance
        self.components_ = W.T
        return self


class PrototypeClassifier():
    def __init__(self):
        pass

    def fit(self, X, y):
        n_components = X.shape[1]
        self.prototypes_labels = unique(y)
        self.n_classes = self.prototypes_labels.shape[0]
        self.prototypes = zeros((self.n_classes, n_components))

        for i in range(self.n_classes):
            label = self.prototypes_labels[i]
            X_with_specific_label = X[y == label, :]
            self.prototypes[i, :] = mean(X_with_specific_label, axis=0).reshape((1, n_components))
        return self

    def predict(self, X):
        # classify using Euclidean metric
        n_test_samples, n_features = X.shape
        n_classes = self.n_classes
        # euclidean_distance = dot(X, self.prototypes.T)
        euclidean_distance = zeros((n_test_samples, n_classes))
        for i in range(n_classes):
            diff = X - dot(ones((n_test_samples, 1)), self.prototypes[i, :].reshape((1, n_features)))
            euclidean_distance[:, i] = sum(diff ** 2, axis=1)

        y_pred = euclidean_distance.argmax(axis=1)
        return y_pred


def plot_gallery(images, titles, h, w, n_row=3, n_col=4):
    """Helper function to plot a gallery of portraits"""
    plt.figure(figsize=(1.8 * n_col, 2.4 * n_row))
    plt.subplots_adjust(bottom=0, left=.01, right=.99, top=.90, hspace=.35)
    for i in range(n_row * n_col):
        plt.subplot(n_row, n_col, i + 1)
        plt.imshow(images[i].reshape((h, w)), cmap=plt.cm.gray)
        plt.title(titles[i], size=12)
        plt.xticks(())
        plt.yticks(())


def title(y_pred, y_test, target_names, i):
    pred_name = target_names[y_pred[i]].rsplit(' ', 1)[-1]
    true_name = target_names[y_test[i]].rsplit(' ', 1)[-1]
    return 'predicted: %s\ntrue:      %s' % (pred_name, true_name)


def main():
    print(__doc__)

    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


###############################################################################
    # Download the data, if not already on disk and load it as numpy arrays

    lfw_people = fetch_lfw_people(min_faces_per_person=100, resize=0.4)

    # introspect the images arrays to find the shapes (for plotting)
    n_samples, h, w = lfw_people.images.shape

    # for machine learning we use the 2 data directly (as relative pixel
    # positions info is ignored by this model)
    X = lfw_people.data
    n_features = X.shape[1]

    # the label to predict is the id of the person
    y = lfw_people.target
    target_names = lfw_people.target_names
    n_classes = target_names.shape[0]

    print("Total dataset size:")
    print("n_samples: %d" % n_samples)
    print("n_features: %d" % n_features)
    print("n_classes: %d" % n_classes)


    ###############################################################################
    # Split into a training set and a test set using a stratified k fold

    # split into a training and testing set
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25)

    n_train_samples = X_train.shape[0]
    n_test_samples = X_test.shape[0]

    ###############################################################################
    # legacy PCA: just computes all the eigenvectors of the training data
    # then select eigenvectors that have the highest eigenvalues

    legacy_PCA_demo = False
    if legacy_PCA_demo:
        n_components = 150

        print("Extracting the top %d eigenfaces from %d faces using legacy PCA"
              % (n_components, X_train.shape[0]))
        t0 = time()
        pca = LegacyPCA(n_components=n_components, whiten=True).fit(X_train)
        print("done in %0.3fs" % (time() - t0))

        print("Projecting the input data on the eigenfaces orthonormal basis")
        t0 = time()
        X_train_pca_legacy = pca.transform(X_train)
        X_test_pca_legacy = pca.transform(X_test)
        print("done in %0.3fs" % (time() - t0))

        print("Fitting the Prototype classifier to the training set using legacy PCA")
        t0 = time()
        clf = PrototypeClassifier().fit(X_train_pca_legacy, y_train)
        print("done in %0.3fs" % (time() - t0))

        print("Predicting people's names on the test set")
        t0 = time()
        y_pred = clf.predict(X_test_pca_legacy)
        print("done in %0.3fs" % (time() - t0))

        print(classification_report(y_test, y_pred, target_names=target_names))

        print("Fitting the SVM classifier to the training set using legacy PCA")
        t0 = time()
        param_grid = {'C': [1e3, 5e3, 1e4, 5e4, 1e5],
                      'gamma': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1], }
        clf = GridSearchCV(SVC(kernel='rbf', class_weight='auto'), param_grid)
        clf = clf.fit(X_train_pca_legacy, y_train)
        print("done in %0.3fs" % (time() - t0))
        print("Best estimator found by grid search:")
        print(clf.best_estimator_)

        print("Predicting people's names on the test set")
        t0 = time()
        y_pred = clf.predict(X_test_pca_legacy)
        print("done in %0.3fs" % (time() - t0))

        print(classification_report(y_test, y_pred, target_names=target_names))

    ##############################################################################
    # Random PCA
    random_PCA_demo = True
    if random_PCA_demo:
        n_components = 150

        print("Extracting the top %d eigenfaces from %d faces using random PCA"
              % (n_components, X_train.shape[0]))
        t0 = time()
        pca = RandomizedPCA(n_components=n_components, whiten=True).fit(X_train)
        print("done in %0.3fs" % (time() - t0))

        eigenfaces_random = pca.components_.reshape((n_components, h, w))

        print("Projecting the input data on the eigenfaces orthonormal basis")
        t0 = time()
        X_train_pca_random = pca.transform(X_train)
        X_test_pca_random = pca.transform(X_test)
        print("done in %0.3fs" % (time() - t0))

        print("Fitting the Prototype classifier to the training set using random PCA")
        t0 = time()
        clf = PrototypeClassifier().fit(X_train_pca_random, y_train)
        print("done in %0.3fs" % (time() - t0))

        print("Predicting people's names on the test set")
        t0 = time()
        y_pred = clf.predict(X_test_pca_random)
        print("done in %0.3fs" % (time() - t0))

        print(classification_report(y_test, y_pred, target_names=target_names))

        print("Fitting the classifier to the training set using random PCA")
        t0 = time()
        param_grid = {'C': [1e3, 5e3, 1e4, 5e4, 1e5],
                      'gamma': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1], }
        clf = GridSearchCV(SVC(kernel='rbf', class_weight='auto'), param_grid)
        clf = clf.fit(X_train_pca_random, y_train)
        print("done in %0.3fs" % (time() - t0))
        print("Best estimator found by grid search:")
        print(clf.best_estimator_)

        print("Predicting people's names on the test set")
        t0 = time()
        y_pred = clf.predict(X_test_pca_random)
        print("done in %0.3fs" % (time() - t0))

        print(classification_report(y_test, y_pred, target_names=target_names))

    ##############################################################################
    # EM PCA
    em_PCA_demo = True
    if em_PCA_demo:
        n_components = 150

        print("Extracting the top %d eigenfaces from %d faces using random PCA"
              % (n_components, X_train.shape[0]))
        t0 = time()
        pca = EMPCA(n_components=n_components, whiten=True).fit(X_train)
        print("done in %0.3fs" % (time() - t0))

        eigenfaces_em = pca.components_.reshape((n_components, h, w))

        print("Projecting the input data on the eigenfaces orthonormal basis")
        t0 = time()
        X_train_pca_em = pca.transform(X_train)
        X_test_pca_em = pca.transform(X_test)
        print("done in %0.3fs" % (time() - t0))

        print("Fitting the classifier to the training set using EM PCA")
        t0 = time()
        param_grid = {'C': [1e3, 5e3, 1e4, 5e4, 1e5],
                      'gamma': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1], }
        clf = GridSearchCV(SVC(kernel='rbf', class_weight='auto'), param_grid)
        clf = clf.fit(X_train_pca_em, y_train)
        print("done in %0.3fs" % (time() - t0))
        print("Best estimator found by grid search:")
        print(clf.best_estimator_)

        print("Predicting people's names on the test set")
        t0 = time()
        y_pred = clf.predict(X_test_pca_em)
        print("done in %0.3fs" % (time() - t0))

        print(classification_report(y_test, y_pred, target_names=target_names))

    ###############################################################################
    # Classification using prototype and Euclidean metric

    ###############################################################################
    # Classification using support vector machines

    ###############################################################################
    # Qualitative evaluation of the predictions using matplotlib
    eigenfaces_legacy = pca.components_.reshape((n_components, h, w))
    eigenface_titles = ["eigenface %d" % i for i in range(eigenfaces_legacy.shape[0])]
    plot_gallery(eigenfaces_legacy, eigenface_titles, h, w)

if __name__ == "__main__":
    # test code is here
    main()