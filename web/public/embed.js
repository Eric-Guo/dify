/** this file is used to embed the chatbot in a website
 * the difyChatbotConfig should be defined in the html file before this script is included
 * the difyChatbotConfig should contain the token of the chatbot
 * the token can be found in the chatbot settings page
 */

// attention: This JavaScript script must be placed after the <body> element. Otherwise, the script will not work.

;(function () {
  // Constants for DOM element IDs and configuration key
  const configKey = 'difyChatbotConfig'
  const buttonId = 'dify-chatbot-bubble-button'
  const iframeId = 'dify-chatbot-bubble-window'
  const config = window[configKey]
  let isExpanded = false

  // SVG icons for open and close states
  const svgIcons = `<svg id="openIcon" width="100%" height="100%" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;">
        <g transform="matrix(0.119037,0,0,0.119142,0.136472,0.0881783)">
            <circle cx="100" cy="100" r="98" style="fill:white;stroke:black;stroke-width:4px;"/>
            <path d="M60,40C86.667,20 113.333,20 140,40C150,60 150,120 140,160L130,180L70,180L60,160C50,120 50,60 60,40Z" style="fill-rule:nonzero;"/>
            <circle cx="100" cy="80" r="50" style="fill:rgb(255,224,214);"/>
            <path d="M70,60C76.667,56.667 83.333,56.667 90,60" style="fill:none;fill-rule:nonzero;stroke:rgb(139,90,43);stroke-width:3px;"/>
            <path d="M110,60C116.667,56.667 123.333,56.667 130,60" style="fill:none;fill-rule:nonzero;stroke:rgb(139,90,43);stroke-width:3px;"/>
            <circle cx="80" cy="75" r="8"/>
            <circle cx="120" cy="75" r="8"/>
            <circle cx="82" cy="73" r="2" style="fill:white;"/>
            <circle cx="122" cy="73" r="2" style="fill:white;"/>
            <path d="M90,95C96.667,98.333 103.333,98.333 110,95" style="fill:none;fill-rule:nonzero;stroke:black;stroke-width:2px;"/>
            <ellipse cx="65" cy="85" rx="8" ry="5" style="fill:rgb(255,192,203);fill-opacity:0.5;"/>
            <ellipse cx="135" cy="85" rx="8" ry="5" style="fill:rgb(255,192,203);fill-opacity:0.5;"/>
            <path d="M60,70C56.667,76.667 56.667,83.333 60,90" style="fill:rgb(255,224,214);fill-rule:nonzero;"/>
            <path d="M140,70C143.333,76.667 143.333,83.333 140,90" style="fill:rgb(255,224,214);fill-rule:nonzero;"/>
            <circle cx="55" cy="75" r="5" style="fill:rgb(192,192,192);"/>
            <path d="M145,74.996L145,75.004C145,77.762 142.76,80 140,80C137.24,80 135,77.762 135,75.004L135,74.996C135,72.238 137.24,70 140,70C142.76,70 145,72.238 145,74.996Z" style="fill:rgb(192,192,192);"/>
            <circle cx="140" cy="75" r="2" style="fill:rgb(136,136,136);"/>
            <rect x="80" y="120" width="40" height="30" style="fill:white;"/>
            <path d="M90,120C96.667,116.667 103.333,116.667 110,120" style="fill:white;fill-rule:nonzero;"/>
            <path d="M70,120C76.667,116.667 83.333,116.667 90,120L80,150L60,150L70,120Z" style="fill-rule:nonzero;"/>
            <path d="M130,120C123.333,116.667 116.667,116.667 110,120L120,150L140,150L130,120Z" style="fill-rule:nonzero;"/>
        </g>
    </svg>
    <svg id="closeIcon" style="display:none" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M18 18L6 6M6 18L18 6" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    `

  const originalIframeStyleText = `
    position: absolute;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    top: unset;
    right: var(--${buttonId}-right, 1rem); /* Align with dify-chatbot-bubble-button. */
    bottom: var(--${buttonId}-bottom, 1rem); /* Align with dify-chatbot-bubble-button. */
    left: unset;
    width: 24rem;
    max-width: calc(100vw - 2rem);
    height: 43.75rem;
    max-height: calc(100vh - 6rem);
    border: none;
    border-radius: 1rem;
    z-index: 2147483640;
    overflow: hidden;
    user-select: none;
    transition-property: width, height;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 150ms;
  `

  const expandedIframeStyleText = `
    position: absolute;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    top: unset;
    right: var(--${buttonId}-right, 1rem); /* Align with dify-chatbot-bubble-button. */
    bottom: var(--${buttonId}-bottom, 1rem); /* Align with dify-chatbot-bubble-button. */
    left: unset;
    min-width: 48rem;
    width: 48%;
    max-width: 40rem; /* Match mobile breakpoint*/
    min-height: 43.75rem;
    height: 88%;
    max-height: calc(100vh - 6rem);
    border: none;
    border-radius: 1rem;
    z-index: 2147483640;
    overflow: hidden;
    user-select: none;
    transition-property: width, height;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 150ms;
  `

  // Main function to embed the chatbot
  async function embedChatbot() {
    let isDragging = false

    if (!config || !config.token) {
      console.error(`${configKey} is empty or token is not provided`)
      return
    }

    async function compressAndEncodeBase64(input) {
      const uint8Array = new TextEncoder().encode(input)
      const compressedStream = new Response(
        new Blob([uint8Array]).stream().pipeThrough(new CompressionStream('gzip')),
      ).arrayBuffer()
      const compressedUint8Array = new Uint8Array(await compressedStream)
      return btoa(String.fromCharCode(...compressedUint8Array))
    }

    async function getCompressedInputsFromConfig() {
      const inputs = config?.inputs || {}
      const compressedInputs = {}
      await Promise.all(
        Object.entries(inputs).map(async ([key, value]) => {
          compressedInputs[key] = await compressAndEncodeBase64(value)
        }),
      )
      return compressedInputs
    }

    async function getCompressedSystemVariablesFromConfig() {
      const systemVariables = config?.systemVariables || {}
      const compressedSystemVariables = {}
      await Promise.all(
        Object.entries(systemVariables).map(async ([key, value]) => {
          compressedSystemVariables[`sys.${key}`] = await compressAndEncodeBase64(value)
        }),
      )
      return compressedSystemVariables
    }

    async function getCompressedUserVariablesFromConfig() {
      const userVariables = config?.userVariables || {}
      const compressedUserVariables = {}
      await Promise.all(
        Object.entries(userVariables).map(async ([key, value]) => {
          compressedUserVariables[`user.${key}`] = await compressAndEncodeBase64(value)
        }),
      )
      return compressedUserVariables
    }

    const params = new URLSearchParams({
      ...(await getCompressedInputsFromConfig()),
      ...(await getCompressedSystemVariablesFromConfig()),
      ...(await getCompressedUserVariablesFromConfig()),
    })

    const baseUrl = config.baseUrl || `https://${config.isDev ? 'dev.' : ''}udify.app`
    const routeSegment = (config.routeSegment || 'chatbot').replace(/^\/+|\/+$/g, '') || 'chatbot'
    const targetOrigin = new URL(baseUrl).origin

    // Pass sendOnEnter config as URL parameter
    if (config.sendOnEnter === false) {
      params.set('sendOnEnter', 'false')
    }

    // pre-check the length of the URL
    const iframeUrl = `${baseUrl}/${routeSegment}/${config.token}?${params}`
    // 1) CREATE the iframe immediately, so it can load in the background:
    const preloadedIframe = createIframe()
    // 2) HIDE it by default:
    preloadedIframe.style.display = 'none'
    // 3) APPEND it to the document body right away:
    document.body.appendChild(preloadedIframe)
    // ─── End Fix Snippet
    if (iframeUrl.length > 2048) {
      console.error(
        'The URL is too long, please reduce the number of inputs to prevent the bot from failing to load',
      )
    }

    // Function to create the iframe for the chatbot
    function createIframe() {
      const iframe = document.createElement('iframe')
      iframe.allow = 'fullscreen;microphone;clipboard-write'
      iframe.title = 'dify chatbot bubble window'
      iframe.id = iframeId
      iframe.src = iframeUrl
      iframe.style.cssText = originalIframeStyleText

      return iframe
    }

    // Function to reset the iframe position
    function resetIframePosition() {
      if (window.innerWidth <= 640) return

      const targetIframe = document.getElementById(iframeId)
      const targetButton = document.getElementById(buttonId)
      if (targetIframe && targetButton) {
        const buttonRect = targetButton.getBoundingClientRect()
        // We don't necessarily need iframeRect anymore with the center logic

        const viewportCenterY = window.innerHeight / 2
        const buttonCenterY = buttonRect.top + buttonRect.height / 2

        if (buttonCenterY < viewportCenterY) {
          targetIframe.style.top = `var(--${buttonId}-bottom, 1rem)`
          targetIframe.style.bottom = 'unset'
        } else {
          targetIframe.style.bottom = `var(--${buttonId}-bottom, 1rem)`
          targetIframe.style.top = 'unset'
        }

        const viewportCenterX = window.innerWidth / 2
        const buttonCenterX = buttonRect.left + buttonRect.width / 2

        if (buttonCenterX < viewportCenterX) {
          targetIframe.style.left = `var(--${buttonId}-right, 1rem)`
          targetIframe.style.right = 'unset'
        } else {
          targetIframe.style.right = `var(--${buttonId}-right, 1rem)`
          targetIframe.style.left = 'unset'
        }
      }
    }

    function toggleExpand() {
      isExpanded = !isExpanded

      const targetIframe = document.getElementById(iframeId)
      if (!targetIframe) return

      if (isExpanded) {
        targetIframe.style.cssText = expandedIframeStyleText
      } else {
        targetIframe.style.cssText = originalIframeStyleText
      }
      resetIframePosition()
    }

    window.addEventListener('message', (event) => {
      if (event.origin !== targetOrigin) return

      const targetIframe = document.getElementById(iframeId)
      if (!targetIframe || event.source !== targetIframe.contentWindow) return

      if (event.data.type === 'dify-chatbot-iframe-ready') {
        targetIframe.contentWindow?.postMessage(
          {
            type: 'dify-chatbot-config',
            payload: {
              isToggledByButton: true,
              isDraggable: !!config.draggable,
            },
          },
          targetOrigin,
        )
      }

      if (event.data.type === 'dify-chatbot-expand-change') {
        toggleExpand()
      }
    })

    // Function to create the chat button
    function createButton() {
      const containerDiv = document.createElement('div')
      // Apply custom properties from config
      Object.entries(config.containerProps || {}).forEach(([key, value]) => {
        if (key === 'className') {
          containerDiv.classList.add(...value.split(' '))
        } else if (key === 'style') {
          if (typeof value === 'object') {
            Object.assign(containerDiv.style, value)
          } else {
            containerDiv.style.cssText = value
          }
        } else if (typeof value === 'function') {
          containerDiv.addEventListener(key.replace(/^on/, '').toLowerCase(), value)
        } else {
          containerDiv[key] = value
        }
      })

      containerDiv.id = buttonId

      // Add styles for the button
      const styleSheet = document.createElement('style')
      document.head.appendChild(styleSheet)
      styleSheet.sheet.insertRule(`
        #${containerDiv.id} {
          position: fixed;
          bottom: var(--${containerDiv.id}-bottom, 1rem);
          right: var(--${containerDiv.id}-right, 1rem);
          left: var(--${containerDiv.id}-left, unset);
          top: var(--${containerDiv.id}-top, unset);
          width: var(--${containerDiv.id}-width, 48px);
          height: var(--${containerDiv.id}-height, 48px);
          border-radius: var(--${containerDiv.id}-border-radius, 25px);
          background-color: var(--${containerDiv.id}-bg-color, #155EEF);
          box-shadow: var(--${containerDiv.id}-box-shadow, rgba(0, 0, 0, 0.2) 0px 4px 8px 0px);
          cursor: pointer;
          z-index: 2147483647;
        }
      `)

      // Create display div for the button icon
      const displayDiv = document.createElement('div')
      displayDiv.style.cssText =
        'position: relative; display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; z-index: 2147483647;'
      displayDiv.innerHTML = svgIcons
      containerDiv.appendChild(displayDiv)
      document.body.appendChild(containerDiv)

      // Add click event listener to toggle chatbot
      containerDiv.addEventListener('click', handleClick)
      // Add touch event listener
      containerDiv.addEventListener(
        'touchend',
        (event) => {
          event.preventDefault()
          handleClick()
        },
        { passive: false },
      )

      function handleClick() {
        if (isDragging) return

        const targetIframe = document.getElementById(iframeId)
        if (!targetIframe) {
          containerDiv.appendChild(createIframe())
          resetIframePosition()
          this.title = 'Exit (ESC)'
          setSvgIcon('close')
          document.addEventListener('keydown', handleEscKey)
          return
        }
        targetIframe.style.display = targetIframe.style.display === 'none' ? 'block' : 'none'
        if (targetIframe.style.display === 'none') {
          setSvgIcon('open')
        } else {
          setSvgIcon('close')
        }

        if (targetIframe.style.display === 'none') {
          document.removeEventListener('keydown', handleEscKey)
        } else {
          document.addEventListener('keydown', handleEscKey)
        }

        resetIframePosition()
      }

      // Enable dragging if specified in config
      if (config.draggable) {
        enableDragging(containerDiv, config.dragAxis || 'both')
      }
    }

    // Function to enable dragging of the chat button
    function enableDragging(element, axis) {
      let startX, startY, startClientX, startClientY

      element.addEventListener('mousedown', startDragging)
      element.addEventListener('touchstart', startDragging)

      function startDragging(e) {
        isDragging = false
        if (e.type === 'touchstart') {
          startX = e.touches[0].clientX - element.offsetLeft
          startY = e.touches[0].clientY - element.offsetTop
          startClientX = e.touches[0].clientX
          startClientY = e.touches[0].clientY
        } else {
          startX = e.clientX - element.offsetLeft
          startY = e.clientY - element.offsetTop
          startClientX = e.clientX
          startClientY = e.clientY
        }
        document.addEventListener('mousemove', drag)
        document.addEventListener('touchmove', drag, { passive: false })
        document.addEventListener('mouseup', stopDragging)
        document.addEventListener('touchend', stopDragging)
        e.preventDefault()
      }

      function drag(e) {
        const touch = e.type === 'touchmove' ? e.touches[0] : e
        const deltaX = touch.clientX - startClientX
        const deltaY = touch.clientY - startClientY

        // Determine whether it is a drag operation
        if (Math.abs(deltaX) > 8 || Math.abs(deltaY) > 8) {
          isDragging = true
        }

        if (!isDragging) return

        element.style.transition = 'none'
        element.style.cursor = 'grabbing'

        // Hide iframe while dragging
        const targetIframe = document.getElementById(iframeId)
        if (targetIframe) {
          targetIframe.style.display = 'none'
          setSvgIcon('open')
        }

        let newLeft, newBottom
        if (e.type === 'touchmove') {
          newLeft = e.touches[0].clientX - startX
          newBottom = window.innerHeight - e.touches[0].clientY - startY
        } else {
          newLeft = e.clientX - startX
          newBottom = window.innerHeight - e.clientY - startY
        }

        const elementRect = element.getBoundingClientRect()
        const maxX = window.innerWidth - elementRect.width
        const maxY = window.innerHeight - elementRect.height

        // Update position based on drag axis
        if (axis === 'x' || axis === 'both') {
          element.style.setProperty(
            `--${buttonId}-left`,
            `${Math.max(0, Math.min(newLeft, maxX))}px`,
          )
        }

        if (axis === 'y' || axis === 'both') {
          element.style.setProperty(
            `--${buttonId}-bottom`,
            `${Math.max(0, Math.min(newBottom, maxY))}px`,
          )
        }
      }

      function stopDragging() {
        setTimeout(() => {
          isDragging = false
        }, 0)
        element.style.transition = ''
        element.style.cursor = 'pointer'

        document.removeEventListener('mousemove', drag)
        document.removeEventListener('touchmove', drag)
        document.removeEventListener('mouseup', stopDragging)
        document.removeEventListener('touchend', stopDragging)
      }
    }

    // Create the chat button if it doesn't exist
    if (!document.getElementById(buttonId)) {
      createButton()
    }
  }

  function setSvgIcon(type = 'open') {
    if (type === 'open') {
      document.getElementById('openIcon').style.display = 'block'
      document.getElementById('closeIcon').style.display = 'none'
    } else {
      document.getElementById('openIcon').style.display = 'none'
      document.getElementById('closeIcon').style.display = 'block'
    }
  }

  // Add esc Exit keyboard event triggered
  function handleEscKey(event) {
    if (event.key === 'Escape') {
      const targetIframe = document.getElementById(iframeId)
      if (targetIframe && targetIframe.style.display !== 'none') {
        targetIframe.style.display = 'none'
        setSvgIcon('open')
      }
    }
  }
  document.addEventListener('keydown', handleEscKey)

  // Set the embedChatbot function to run when the body is loaded,Avoid infinite nesting
  if (config?.dynamicScript) {
    embedChatbot()
  } else {
    document.body.onload = embedChatbot
  }
})()
