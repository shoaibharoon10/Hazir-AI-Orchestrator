package com.example.orchestrator

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : AppCompatActivity() {

    private lateinit var queryInput: TextInputEditText
    private lateinit var orchestrateBtn: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var errorText: TextView
    private lateinit var resultsContainer: View
    private lateinit var intentText: TextView
    private lateinit var matchText: TextView
    private lateinit var priceText: TextView
    private lateinit var bookingText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        queryInput = findViewById(R.id.queryInput)
        orchestrateBtn = findViewById(R.id.orchestrateBtn)
        progressBar = findViewById(R.id.progressBar)
        errorText = findViewById(R.id.errorText)
        resultsContainer = findViewById(R.id.resultsContainer)
        intentText = findViewById(R.id.intentText)
        matchText = findViewById(R.id.matchText)
        priceText = findViewById(R.id.priceText)
        bookingText = findViewById(R.id.bookingText)

        orchestrateBtn.setOnClickListener {
            val query = queryInput.text.toString().trim()
            if (query.isNotEmpty()) {
                executeOrchestration(query)
            }
        }
    }

    private fun executeOrchestration(query: String) {
        // Reset UI
        errorText.visibility = View.GONE
        resultsContainer.visibility = View.GONE
        progressBar.visibility = View.VISIBLE
        orchestrateBtn.isEnabled = false

        CoroutineScope(Dispatchers.IO).launch {
            try {
                // 10.0.2.2 is the special alias to your host loopback interface in Android Emulator
                val url = URL("http://10.0.2.2:8000/api/orchestrate/run-all")
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.setRequestProperty("Accept", "application/json")
                connection.doOutput = true

                val jsonPayload = JSONObject()
                jsonPayload.put("query", query)
                jsonPayload.put("customer_id", "CUST-MOB-001")
                jsonPayload.put("user_location", "Clifton Block 9")

                val outputWriter = OutputStreamWriter(connection.outputStream)
                outputWriter.write(jsonPayload.toString())
                outputWriter.flush()
                outputWriter.close()

                val responseCode = connection.responseCode
                val stream = if (responseCode in 200..299) connection.inputStream else connection.errorStream
                
                val reader = BufferedReader(InputStreamReader(stream))
                val responseString = reader.readText()
                reader.close()

                val responseJson = JSONObject(responseString)

                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.GONE
                    orchestrateBtn.isEnabled = true

                    if (responseCode in 200..299 && responseJson.getBoolean("success")) {
                        populateResults(responseJson.getJSONObject("data"))
                    } else {
                        showError(responseJson)
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    progressBar.visibility = View.GONE
                    orchestrateBtn.isEnabled = true
                    errorText.visibility = View.VISIBLE
                    errorText.text = "Network Error: ${e.message}\nMake sure backend is running on port 8000."
                }
            }
        }
    }

    private fun populateResults(data: JSONObject) {
        resultsContainer.visibility = View.VISIBLE
        
        // 1. Intent Extraction
        if (data.has("parsed_intent")) {
            val intent = data.getJSONObject("parsed_intent")
            val conf = (intent.getDouble("confidence_score") * 100).toInt()
            intentText.text = "1. INTENT EXTRACTION\n" +
                    "Category: ${intent.getString("service_category")}\n" +
                    "Location: ${intent.getString("location_context")}\n" +
                    "Urgency: ${intent.getString("urgency_level").uppercase()}\n" +
                    "Confidence: $conf%"
        }

        // 2. Matching
        if (data.has("assigned_provider")) {
            val provider = data.getJSONObject("assigned_provider")
            matchText.text = "2. PROVIDER MATCHING\n" +
                    "Name: ${provider.getString("name")}\n" +
                    "Distance: ${provider.getDouble("distance_km")} km\n" +
                    "Score: ${provider.getDouble("composite_score")}"
        }

        // 3. Pricing
        if (data.has("price_breakdown")) {
            val price = data.getJSONObject("price_breakdown")
            priceText.text = "3. DYNAMIC PRICING\n" +
                    "Base: PKR ${price.getDouble("base_price")}\n" +
                    "Surge: + PKR ${price.getDouble("surge_cost")}\n" +
                    "Net Total: PKR ${price.getDouble("net_total")}"
        }

        // 4. Booking
        if (data.has("booking_summary")) {
            val booking = data.getJSONObject("booking_summary")
            bookingText.text = "4. BOOKING CONFIRMED\n" +
                    "ID: ${booking.getString("booking_id")}\n" +
                    "State: ${booking.getString("current_status").uppercase()}"
        }
    }

    private fun showError(responseJson: JSONObject) {
        errorText.visibility = View.VISIBLE
        val errorMsg = responseJson.optString("error", "Transaction Failed")
        
        var details = ""
        if (responseJson.has("data")) {
            val errorData = responseJson.getJSONObject("data")
            if (errorData.has("error_stage")) {
                details += "\nStage: ${errorData.getString("error_stage").uppercase()}"
            }
            if (errorData.has("message")) {
                details += "\nReason: ${errorData.getString("message")}"
            }
        }
        
        errorText.text = "$errorMsg$details"
    }
}
