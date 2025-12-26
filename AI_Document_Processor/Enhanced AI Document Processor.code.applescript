property maxRetries : 3
property chunkSize : 3000  # Characters per API call
property qualityThreshold : 0.7  # Minimum confidence score

on aiProcessChunk(inputText, feature, apiKey)
    set prompt to my buildPrompt(feature, inputText)
    set retryCount to 0
    
    repeat while retryCount < maxRetries
        try
            set response to do shell script "curl -s -X POST " & aiEndpoint & " \\
                -H 'Content-Type: application/json' \\
                -H 'Authorization: Bearer " & apiKey & "' \\
                -d '{\"model\":\"" & aiModel & "\", \"messages\":[{\"role\":\"user\",\"content\":\"" & prompt & "\"}]}'"
            
            set jsonResponse to my parseJSON(response)
            if confidenceScore of jsonResponse > qualityThreshold then
                return content of jsonResponse
            end if
            
        on error errMsg
            log "API Error: " & errMsg
            delay (2 ^ retryCount)  # Exponential backoff
            set retryCount to retryCount + 1
        end try
    end repeat
    return inputText  # Fallback
end aiProcessChunk

on buildPrompt(feature, text)
  set featurePrompts to {¬
      "Auto Language Detection": "Identify primary language (ISO 639-1 code only). Text: «text»", ¬
      "Technical Explanation": "Explain technical terms inline [like this]. Text: «text»", ¬
      "Bilingual Analysis": "Create EN-BN parallel annotations. Text: «text»", ¬
      "Formatting Optimization": "Optimize document structure with markdown formatting. Text: «text»"}
  return replaceText(featurePrompts's feature, "«text»", text)
end buildPrompt