import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { registerUser } from "../services";
import "../styles/dashboard.css";

type RegisterFormData = {
    fullName: string;
    username: string;
    password: string;
    email: string;
    phone: string;
};

type FormErrors = Partial<Record<keyof RegisterFormData, string>>;

const initialFormData: RegisterFormData = {
    fullName: "",
    username: "",
    password: "",
    email: "",
    phone: "",
};

export function RegisterPage() {
    const [formData, setFormData] = useState<RegisterFormData>(initialFormData);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");
    const [touched, setTouched] = useState<Partial<Record<keyof RegisterFormData, boolean>>>({});

    function validate(values: RegisterFormData): FormErrors {
        const errors: FormErrors = {};

        if (!values.fullName.trim()) {
            errors.fullName = "Full name is required.";
        }

        if (!values.username.trim()) {
            errors.username = "Username is required.";
        } else if (values.username.trim().length < 3) {
            errors.username = "Username must be at least 3 characters.";
        }

        if (!values.email.trim()) {
            errors.email = "Email is required.";
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
            errors.email = "Enter a valid email address.";
        }

        if (!values.phone.trim()) {
            errors.phone = "Phone number is required.";
        } else if (!/^[0-9+\-()\s]{7,20}$/.test(values.phone)) {
            errors.phone = "Enter a valid phone number.";
        }

        if (!values.password) {
            errors.password = "Password is required.";
        } else if (values.password.length < 8) {
            errors.password = "Password must be at least 8 characters.";
        }

        return errors;
    }

    const errors = useMemo(() => validate(formData), [formData]);
    const isFormValid = useMemo(() => Object.keys(errors).length === 0, [errors]);

    function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        const { name, value } = event.target;

        setFormData((prevData) => ({
            ...prevData,
            [name]: value,
        }));

        setErrorMessage("");
        setSuccessMessage("");
    }

    function handleBlur(event: React.FocusEvent<HTMLInputElement>) {
        const { name } = event.target;
        setTouched((prev) => ({
            ...prev,
            [name]: true,
        }));
    }

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        const nextTouched: Partial<Record<keyof RegisterFormData, boolean>> = {
            fullName: true,
            username: true,
            email: true,
            phone: true,
            password: true,
        };
        setTouched(nextTouched);

        const validationErrors = validate(formData);
        if (Object.keys(validationErrors).length > 0) {
            setErrorMessage("Please fix the highlighted fields.");
            return;
        }

        setLoading(true);
        setErrorMessage("");
        setSuccessMessage("");

        try {
            await registerUser({
                fullName: formData.fullName.trim(),
                username: formData.username.trim(),
                password: formData.password,
                email: formData.email.trim(),
                phone: formData.phone.trim(),
            });

            setSuccessMessage("Registration successful. You can now log in.");
            setFormData(initialFormData);
            setTouched({});
        } catch (error: any) {
            console.error("Registration failed:", error);
            setErrorMessage(
                error?.response?.data?.message ||
                error?.message ||
                "Registration failed. Please try again."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Create account</h1>
                <p>Register for the rental market workspace.</p>

                <form onSubmit={handleSubmit} className="auth-form" noValidate>
                    <div>
                        <label htmlFor="fullName">Full Name</label>
                        <input
                            id="fullName"
                            type="text"
                            name="fullName"
                            autoComplete="name"
                            value={formData.fullName}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            aria-invalid={!!(touched.fullName && errors.fullName)}
                            aria-describedby={touched.fullName && errors.fullName ? "fullName-error" : undefined}
                        />
                        {touched.fullName && errors.fullName && (
                            <p id="fullName-error" className="auth-error">
                                {errors.fullName}
                            </p>
                        )}
                    </div>

                    <div>
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            type="text"
                            name="username"
                            autoComplete="username"
                            value={formData.username}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            aria-invalid={!!(touched.username && errors.username)}
                            aria-describedby={touched.username && errors.username ? "username-error" : undefined}
                        />
                        {touched.username && errors.username && (
                            <p id="username-error" className="auth-error">
                                {errors.username}
                            </p>
                        )}
                    </div>

                    <div>
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            name="email"
                            autoComplete="email"
                            value={formData.email}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            aria-invalid={!!(touched.email && errors.email)}
                            aria-describedby={touched.email && errors.email ? "email-error" : undefined}
                        />
                        {touched.email && errors.email && (
                            <p id="email-error" className="auth-error">
                                {errors.email}
                            </p>
                        )}
                    </div>

                    <div>
                        <label htmlFor="phone">Phone</label>
                        <input
                            id="phone"
                            type="tel"
                            name="phone"
                            autoComplete="tel"
                            value={formData.phone}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            aria-invalid={!!(touched.phone && errors.phone)}
                            aria-describedby={touched.phone && errors.phone ? "phone-error" : undefined}
                        />
                        {touched.phone && errors.phone && (
                            <p id="phone-error" className="auth-error">
                                {errors.phone}
                            </p>
                        )}
                    </div>

                    <div>
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            name="password"
                            autoComplete="new-password"
                            value={formData.password}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            aria-invalid={!!(touched.password && errors.password)}
                            aria-describedby={touched.password && errors.password ? "password-error" : undefined}
                        />
                        {touched.password && errors.password && (
                            <p id="password-error" className="auth-error">
                                {errors.password}
                            </p>
                        )}
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

                    <button type="submit" disabled={loading || !isFormValid}>
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