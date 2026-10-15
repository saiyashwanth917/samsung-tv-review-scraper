
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Samsung TV Review Scraper",
    page_icon="📺",
    layout="wide"
)

# -------------------------------
# Application Title
# -------------------------------
st.title("📺 Samsung TV Review Scraper")
st.write(
    "Extract customer reviews from a Samsung TV product page "
    "and download the results as a CSV file."
)

st.info(
    "This application can collect reviews present in the webpage HTML. "
    "Some reviews may not be accessible if Samsung loads them dynamically."
)

# -------------------------------
# Product URL
# -------------------------------
url = st.text_input(
    "Samsung TV Product URL",
    value=(
        "https://www.samsung.com/in/tvs/"
        "oled-tv/s85h-55-inch-oled-4k-smart-tv-qa55s85haelxl/"
    )
)

# -------------------------------
# Number of Reviews
# -------------------------------
max_reviews = st.number_input(
    "Maximum reviews",
    min_value=1,
    max_value=44,
    value=44,
    step=1
)

# -------------------------------
# Fetch Reviews
# -------------------------------
if st.button("Fetch Reviews", type="primary"):

    if not url.strip().startswith(("https://", "http://")):
        st.error("Please enter a valid product URL.")
        st.stop()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        with st.spinner("Fetching Samsung TV reviews..."):

            response = requests.get(
                url.strip(),
                headers=headers,
                timeout=25
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # Possible review selectors
            selectors = [
                "div.pdd44-review__contents-detail-text",
                "#bvreviews .bv-content-summary-body-text",
                "#bvreviews .bv-content-review"
            ]

            review_elements = []

            for selector in selectors:
                review_elements = soup.select(selector)

                if review_elements:
                    break

            # Extract unique review text
            reviews = []

            for element in review_elements:

                review_text = element.get_text(
                    separator=" ",
                    strip=True
                )

                if review_text and review_text not in reviews:
                    reviews.append(review_text)

                if len(reviews) >= int(max_reviews):
                    break

        # -------------------------------
        # Display Results
        # -------------------------------
        if reviews:

            df = pd.DataFrame({
                "Review": reviews
            })

            st.success(
                f"Successfully collected {len(reviews)} reviews."
            )

            st.subheader("Customer Reviews")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # Download as CSV
            csv_data = df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="📥 Download Reviews as CSV",
                data=csv_data,
                file_name="Samsung_TV_Reviews.csv",
                mime="text/csv"
            )

        else:

            st.warning(
                "No reviews were found in the webpage HTML. "
                "Samsung may load reviews through JavaScript, "
                "or the HTML selectors may need updating."
            )

            st.write(
                "Try another product page or inspect the webpage "
                "to identify the correct review selectors."
            )

    except requests.exceptions.Timeout:

        st.error(
            "The request timed out. Please try again later."
        )

    except requests.exceptions.HTTPError as error:

        st.error(
            f"Samsung returned an HTTP error: {error}"
        )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Unable to fetch the webpage: {error}"
        )

    except Exception as error:

        st.error(
            f"An unexpected error occurred: {error}"
        )

# -------------------------------
# Footer
# -------------------------------
st.divider()

st.caption(
    "Samsung TV Review Scraper | Built with Python, "
    "Streamlit, BeautifulSoup and Pandas"
)
