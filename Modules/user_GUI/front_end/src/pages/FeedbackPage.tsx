import React, { useState } from "react";
import { submitFeedback } from "../services";
import "../styles/dashboard.css";

export function FeedbackPage() {
    const [rating, setRating] = useState(0);
    const [hovered, setHovered] = useState(0);
    const [comment, setComment] = useState("");
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setErrorMessage("");
        setSuccessMessage("");

        if (rating < 1 || rating > 5) {
            setErrorMessage("Please choose a star rating from 1 to 5.");
            return;
        }

        setLoading(true);
        try {
            await submitFeedback({
                rating,
                comment: comment.trim(),
            });

            setSuccessMessage(`Thanks — your ${rating}-star feedback was saved.`);
        } catch (error: any) {
            console.error("Feedback submit failed:", error);
            setErrorMessage(error?.message || "Unable to save feedback right now.");
        } finally {
            setLoading(false);
        }
    }

    const displayRating = hovered || rating;

    return (
        <div className="dashboard-panel feedback-panel">
            <p>Rate the app and leave comments about UI, scraper behavior, and data quality.</p>

            <form onSubmit={handleSubmit} className="feedback-form" noValidate>
                <div className="feedback-field">
                    <label className="feedback-label">Star rating</label>

                    <div className="feedback-stars-wrap">
                        <div className="feedback-stars" role="radiogroup" aria-label="Star rating">
                            {[1, 2, 3, 4, 5].map((star) => {
                                const active = star <= displayRating;

                                return (
                                    <button
                                        key={star}
                                        type="button"
                                        className={`star-button ${active ? "active" : ""}`}
                                        onClick={() => setRating(star)}
                                        onMouseEnter={() => setHovered(star)}
                                        onMouseLeave={() => setHovered(0)}
                                        aria-label={`Rate ${star} star${star > 1 ? "s" : ""}`}
                                        aria-pressed={rating === star}
                                    >
                                        ★
                                    </button>
                                );
                            })}
                        </div>

                        <span className="feedback-rating-text">
                            {rating > 0 ? `${rating}/5 selected` : "No rating yet"}
                        </span>
                    </div>
                </div>

                <div className="feedback-field">
                    <label htmlFor="feedback-comment" className="feedback-label">
                        Comments
                    </label>
                    <textarea
                        id="feedback-comment"
                        name="comment"
                        className="feedback-textarea"
                        rows={5}
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Share UI issues, scraper observations, missing features, or data-quality problems."
                    />
                </div>

                {errorMessage && (
                    <p className="auth-error" role="alert">
                        {errorMessage}
                    </p>
                )}

                {successMessage && (
                    <p className="auth-success" role="status">
                        {successMessage}
                    </p>
                )}

                <button className="feedback-submit" type="submit" disabled={loading}>
                    {loading ? "Saving..." : "Submit feedback"}
                </button>
            </form>
        </div>
    );
}