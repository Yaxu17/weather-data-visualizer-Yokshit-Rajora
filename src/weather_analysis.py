# src/weather_analysis.py

from pathlib import Path
import sys
import traceback

# Use non-interactive backend so savefig doesn't require a GUI or IPython backend.
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

# ---------------------------
# Configuration / Paths
# ---------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # parent of src/ is project root
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = PROJECT_ROOT / "images"
REPORTS_DIR = PROJECT_ROOT / "reports"

RAW_CSV = DATA_DIR / "raw_weather.csv"
CLEANED_CSV = DATA_DIR / "cleaned_weather.csv"

# filenames for images
IMG_DAILY_TEMP = IMAGES_DIR / "daily_temperature.png"
IMG_MONTHLY_RAIN = IMAGES_DIR / "monthly_rainfall.png"
IMG_HUMID_TEMP = IMAGES_DIR / "humidity_vs_temperature.png"
IMG_COMBINED = IMAGES_DIR / "combined_plots.png"


# ---------------------------
# Utilities
# ---------------------------
def ensure_dirs():
    """Create expected directories if they don't exist."""
    for p in (DATA_DIR, IMAGES_DIR, REPORTS_DIR):
        p.mkdir(parents=True, exist_ok=True)


def read_dataset(path: Path) -> pd.DataFrame:
    """Read CSV into DataFrame and basic validation."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset missing: {path}\nPlace your raw CSV at: {path}"
        )

    df = pd.read_csv(path)
    if "Date" not in df.columns:
        raise KeyError("CSV must contain a 'Date' column.")
    # Basic expected columns check (but be flexible)
    required = {"Date", "Temperature", "Rainfall", "Humidity"}
    missing = required - set(df.columns)
    if missing:
        print(f"Warning: CSV is missing columns: {missing}. Script will try to continue.")
    return df


def safe_savefig(fig_path: Path):
    """Helper to ensure parent exists then save. (fig_path is Path)"""
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    # matplotlib will save the current figure if plt.savefig used, but here we use plt directly
    # Caller should call plt.savefig(fig_path) right after preparing the figure.


# ---------------------------
# Analysis pipeline
# ---------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the input dataframe and return cleaned copy."""
    df = df.copy()
    # Convert Date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if df["Date"].isna().any():
        print("Warning: Some 'Date' values could not be parsed and became NaT. Dropping those rows.")
        df = df.dropna(subset=["Date"])

    # Ensure numeric columns
    for col in ["Temperature", "Rainfall", "Humidity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing values with reasonable defaults
    if "Temperature" in df.columns:
        temp_mean = df["Temperature"].mean(skipna=True)
        df["Temperature"] = df["Temperature"].fillna(temp_mean)
    if "Rainfall" in df.columns:
        df["Rainfall"] = df["Rainfall"].fillna(0)  # assume missing rainfall -> 0
    if "Humidity" in df.columns:
        hum_median = df["Humidity"].median(skipna=True)
        df["Humidity"] = df["Humidity"].fillna(hum_median)

    # Keep only relevant columns if they exist
    cols_keep = [c for c in ["Date", "Temperature", "Rainfall", "Humidity"] if c in df.columns]
    df = df[cols_keep]

    # Sort by date
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def compute_statistics(df: pd.DataFrame):
    """Compute and return dictionaries of daily/monthly/yearly stats."""
    stats = {}
    stats["daily"] = df.describe()
    # monthly / yearly require Date index or resample on Date
    monthly = df.resample("M", on="Date").agg(["mean", "min", "max", "std"])
    yearly = df.resample("Y", on="Date").agg(["mean", "min", "max", "std"])
    stats["monthly"] = monthly
    stats["yearly"] = yearly
    return stats


def add_season_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a Season column to dataframe based on month."""
    season_map = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Summer", 4: "Summer", 5: "Summer",
        6: "Monsoon", 7: "Monsoon", 8: "Monsoon",
        9: "Autumn", 10: "Autumn", 11: "Autumn",
    }
    df = df.copy()
    df["Season"] = df["Date"].dt.month.map(season_map)
    return df


# ---------------------------
# Plotting
# ---------------------------
def plot_daily_temperature(df: pd.DataFrame, out_path: Path):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Temperature"], linewidth=1)
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.title("Daily Temperature Trend")
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_monthly_rainfall(df: pd.DataFrame, out_path: Path):
    # Use 'ME' to avoid future deprecation (month-end). If your pandas version doesn't support 'ME',
    # use 'M' and ignore the FutureWarning, or upgrade pandas.
    monthly_rain = df.resample("ME", on="Date")["Rainfall"].sum()

    plt.figure(figsize=(10, 5))
    # Convert index to python datetimes for plotting (DatetimeIndex -> ndarray of datetimes)
    x = monthly_rain.index.to_pydatetime()
    plt.bar(x, monthly_rain.values, width=20)  # width in days; adjust if bars overlap

    plt.xlabel("Month")
    plt.ylabel("Rainfall (mm)")
    plt.title("Monthly Rainfall Totals")

    # Format x-axis nicely
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()



def plot_humidity_vs_temperature(df: pd.DataFrame, out_path: Path):
    plt.figure(figsize=(7, 6))
    plt.scatter(df["Temperature"], df["Humidity"], s=12, alpha=0.7)
    plt.xlabel("Temperature (°C)")
    plt.ylabel("Humidity (%)")
    plt.title("Humidity vs Temperature")
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_combined(df: pd.DataFrame, out_path: Path):
    monthly_rain = df.resample("ME", on="Date")["Rainfall"].sum()
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)

    axes[0].plot(df["Date"], df["Temperature"], linewidth=1)
    axes[0].set_title("Daily Temperature")
    axes[0].set_ylabel("Temperature (°C)")
    axes[0].grid(alpha=0.2)

    x = monthly_rain.index.to_pydatetime()
    axes[1].bar(x, monthly_rain.values, width=20)
    axes[1].set_title("Monthly Rainfall")
    axes[1].set_ylabel("Rainfall (mm)")
    axes[1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    for tick in axes[1].get_xticklabels():
        tick.set_rotation(45)
        tick.set_ha("right")
    axes[1].grid(axis="y", alpha=0.2)

    fig.suptitle("Temperature and Rainfall Overview", fontsize=14)
    fig.savefig(out_path)
    plt.close(fig)



# ---------------------------
# Main runner
# ---------------------------
def main():
    try:
        ensure_dirs()
        print(f"Project root detected at: {PROJECT_ROOT}")
        print(f"Looking for dataset at: {RAW_CSV}")

        df_raw = read_dataset(RAW_CSV)
        print("Loaded dataset rows:", len(df_raw))

        df = clean_data(df_raw)
        print("After cleaning, rows:", len(df))

        # Save cleaned CSV
        CLEANED_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CLEANED_CSV, index=False)
        print("Saved cleaned CSV to:", CLEANED_CSV)

        # Compute stats (and print some summaries)
        stats = compute_statistics(df)
        print("\n-- Daily stats (head) --")
        print(stats["daily"].head())

        print("\n-- Monthly sample (first 5 rows) --")
        print(stats["monthly"].head())

        # Add season col and print season-wise means (if columns exist)
        if {"Temperature", "Humidity", "Rainfall"}.issubset(df.columns):
            df = add_season_column(df)
            season_stats = df.groupby("Season")[["Temperature", "Humidity", "Rainfall"]].mean()
            print("\n-- Season-wise averages --")
            print(season_stats)

        # Plot & save images
        print("\nCreating plots...")
        plot_daily_temperature(df, IMG_DAILY_TEMP)
        print("Saved:", IMG_DAILY_TEMP)

        plot_monthly_rainfall(df, IMG_MONTHLY_RAIN)
        print("Saved:", IMG_MONTHLY_RAIN)

        plot_humidity_vs_temperature(df, IMG_HUMID_TEMP)
        print("Saved:", IMG_HUMID_TEMP)

        plot_combined(df, IMG_COMBINED)
        print("Saved:", IMG_COMBINED)

        print("\nAll done. Check the images/ and data/ folders.")

    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
        print("\nIf this is a FileNotFoundError about raw_weather.csv,")
        print("make sure you placed the dataset at:", RAW_CSV)
        sys.exit(1)


if __name__ == "__main__":
    main()
