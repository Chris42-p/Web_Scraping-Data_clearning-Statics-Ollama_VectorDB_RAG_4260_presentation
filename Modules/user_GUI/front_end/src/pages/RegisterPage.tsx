import React, { useState } from "react";
import { Link } from "react-router-dom";
import { registerUser } from "../services";
import "../styles/dashboard.css";

export function RegisterPage() {
    const [formData, setFormData] = useState({
        fullName: "",
        username: "",
        password: "",
        email: "",
        phone: "",
    });

    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        const { name, value } = event.target;

        setFormData((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    }

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        setLoading(true);
        setErrorMessage("");
        setSuccessMessage("");

        try {
            await registerUser({
                username: formData.username,
                password: formData.password,
            });

            setSuccessMessage("Registration successful. You can now log in.");
        } catch (error) {
            console.error("Registration failed:", error);
            setErrorMessage("Registration failed. Please try again.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Create account</h1>
                <p>Register for the rental market workspace.</p>

                <form onSubmit={handleSubmit} className="auth-form">
                    <div>
                        <label>Full Name</label>
                        <input
                            type="text"
                            name="fullName"
                            value={formData.fullName}
                            onChange={handleChange}
                        />
                    </div>

                    <div>
                        <label>Username</label>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                        />
                    </div>

                    <div>
                        <label>Email</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                        />
                    </div>

                    <div>
                        <label>Phone</label>
                        <input
                            type="tel"
                            name="phone"
                            value={formData.phone}
                            onChange={handleChange}
                        />
                    </div>

                    <div>
                        <label>Password</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                        />
                    </div>

                    {errorMessage && <p className="auth-error">{errorMessage}</p>}
                    {successMessage && <p className="auth-success">{successMessage}</p>}

                    <button type="submit" disabled={loading}>
                        {loading ? "Registering..." : "Register"}
                    </button>
                </form>

                <p className="auth-switch-text">
                    Already have an account? <Link to="/login">Back to login</Link>
                </p>
            </div>
        </div>
    );
}