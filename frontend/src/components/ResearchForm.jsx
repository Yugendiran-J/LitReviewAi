import { useState } from "react";

export default function ResearchForm() {

  const [formData, setFormData] = useState({
    keyword: "",
    domain: "",
    population: "",
    intervention: "",
    comparison: "",
    outcome: "",
    study_type: ""
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {

    setFormData({
      ...formData,
      [event.target.name]: event.target.value
    });

  };

  const handleSubmit = async (event) => {

    event.preventDefault();

    setLoading(true);

    try {

      console.log(
        "Research configuration:",
        formData
      );

      // Backend API will be connected
      // in the next step.

      alert(
        "Research configuration submitted successfully."
      );

    } catch (error) {

      console.error(error);

      alert(
        "Something went wrong."
      );

    } finally {

      setLoading(false);

    }

  };

  return (

    <div className="min-h-screen bg-gray-100 p-6">

      <div className="mx-auto max-w-4xl">

        <div className="mb-8">

          <h1 className="text-3xl font-bold text-gray-900">
            LitReviewAI
          </h1>

          <p className="mt-2 text-gray-600">
            AI-Powered Systematic Literature Review Assistant
          </p>

        </div>


        <div className="rounded-xl bg-white p-8 shadow">

          <h2 className="mb-6 text-2xl font-semibold">
            Create Literature Review
          </h2>


          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >

            {/* Research Topic */}

            <div>

              <label className="mb-2 block font-medium">
                Research Topic
              </label>

              <input
                type="text"
                name="keyword"
                value={formData.keyword}
                onChange={handleChange}
                placeholder="Example: Artificial Intelligence in Systematic Literature Review"
                required
                className="w-full rounded-lg border p-3 outline-none focus:ring-2"
              />

            </div>


            {/* Domain */}

            <div>

              <label className="mb-2 block font-medium">
                Research Domain
              </label>

              <input
                type="text"
                name="domain"
                value={formData.domain}
                onChange={handleChange}
                placeholder="Example: Artificial Intelligence"
                className="w-full rounded-lg border p-3 outline-none focus:ring-2"
              />

            </div>


            {/* Population */}

            <div>

              <label className="mb-2 block font-medium">
                Population
              </label>

              <textarea
                name="population"
                value={formData.population}
                onChange={handleChange}
                placeholder="Who or what is being studied?"
                rows="3"
                className="w-full rounded-lg border p-3 outline-none focus:ring-2"
              />

            </div>


            {/* Intervention */}

            <div>

              <label className="mb-2 block font-medium">
                Intervention
              </label>

              <textarea
                name="intervention"
                value={formData.intervention}
                onChange={handleChange}
                placeholder="What technology, treatment, method, or intervention?"
                rows="3"
                className="w-full rounded-lg border p-3 outline-none focus:ring-2"
              />

            </div>


            {/* Comparison */}

            <div>

              <label className="mb-2 block font-medium">
                Comparison
              </label>

              <textarea
                name="comparison"
                value={formData.comparison}
                onChange={handleChange}
                placeholder="What is the comparison method?"
                rows="3"
                className="w-full rounded-lg border p-3 outline-none focus:ring-2"
              />

            </div>


            {/* Outcome */}

            <div>

              <label className="mb-2 block font-medium">
                Outcome
              </label>

              <textarea
                name="outcome"
                value={formData.outcome}
                onChange={handleChange}
                placeholder="What outcomes are being measured?"
                rows="3"
                className="w-full rounded-lg border p-3 outline-none focus:ring-2"
              />

            </div>


            {/* Study Type */}

            <div>

              <label className="mb-2 block font-medium">
                Study Type
              </label>

              <input
                type="text"
                name="study_type"
                value={formData.study_type}
                onChange={handleChange}
                placeholder="Example: Systematic Review"
                className="w-full rounded-lg border p-3 outline-none focus:ring-2"
              />

            </div>


            {/* Submit */}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-black px-6 py-3 font-semibold text-white"
            >

              {loading
                ? "Starting..."
                : "Start Literature Review"
              }

            </button>

          </form>

        </div>

      </div>

    </div>

  );
}