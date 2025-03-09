import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier

# Load dataset
file_path = "DoctorDatasetcsvfile.csv"  # Adjust file path if necessary
raw_data = pd.read_csv(file_path, sep=';')

# Data Preprocessing
raw_data.columns = raw_data.columns.str.strip()
raw_data[['Doctor Name', 'Specialization', 'Hospital', 'District']] = raw_data[
    'Doctor name ,specialization,Hospital ,district'
].str.split(',', expand=True)
raw_data.drop(columns=['Doctor name ,specialization,Hospital ,district'], inplace=True)

# Encode categorical features
specialization_encoder = LabelEncoder()
district_encoder = LabelEncoder()

raw_data['Specialization_Encoded'] = specialization_encoder.fit_transform(raw_data['Specialization'])
raw_data['District_Encoded'] = district_encoder.fit_transform(raw_data['District'])

# Define features and target
X = raw_data[['Specialization_Encoded', 'District_Encoded']]
y = raw_data['Specialization_Encoded'].apply(lambda x: 1 if x in [0, 1] else 0)  # Dummy target for now

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train the KNN model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_scaled, y)

# Save the model, encoders, and scaler
joblib.dump(knn, "knn_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(specialization_encoder, "label_encoder_specialization.pkl")
joblib.dump(district_encoder, "label_encoder_district.pkl")

print("KNN model and encoders saved successfully!")
